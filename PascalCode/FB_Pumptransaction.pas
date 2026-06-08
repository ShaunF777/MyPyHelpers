(*
    FB_PumpTransaction
    CODESYS 3.5 SP16 Patch 5
    Reusable per-pump function block implementing:
    - Latching pushbutton, RFID latch, popups, timeout supervision
    - Start criteria, 30s flow-start and stall detection
    - 1s dispense supervision and limit stop
    - Transaction write pulse and post-write meter reset pulse

    Author: Shaun + Copilot
*)

FUNCTION_BLOCK FB_PumpTransaction
VAR_INPUT
    (* HMI pushbutton: momentary; this FB toggles an internal latch on rising edges *)
    xPumpPushButton         : BOOL;

    (* RFID approval: momentary TRUE when approved; FB latches internally *)
    xRFIDPopupCheck         : BOOL;

    (* Vehicle approval: set TRUE after vehicle selection popup returns approved *)
    xVehicleApproved        : BOOL;

    (* Live flowmeter reading for this pump *)
    rLiterCountIn           : REAL;

    (* Per-step process timeout (seconds). Default 10s; set per HMI or leave at 10 *)
    usiProcessTimeout_s     : USINT := 10;

    (* Metadata provided by HMI/logic for DB write *)
    sPumpName               : STRING(30);
    sVehicleName            : STRING(30);
    sNameHMI                : STRING(30);
    sCoyNoHMI               : STRING(30);
END_VAR

VAR_IN_OUT
    (* Target liters requested by operator; HMI writes this after popup is requested *)
    rLitersRequested        : REAL;
END_VAR

VAR_OUTPUT
    (* UI/dialog requests *)
    xRequestLitersPopup     : BOOL;    // Ask HMI to open "enter liters" dialog
    xRequestVehiclePopup    : BOOL;    // Ask HMI to open "select vehicle" dialog

    (* Latches and final approval *)
    xRFIDCheckApproved      : BOOL;    // Latched TRUE when RFID approved
    xPumpApproved           : BOOL;    // Drives pump valve/enable (external IO)

    (* Status and diagnostics *)
    xActive                 : BOOL;    // Transaction active (not idle)
    xBusy                   : BOOL;    // Busy executing a step or dispensing
    xError                  : BOOL;    // Faulted state
    sState                  : STRING(50); // Human-readable state
    sError                  : STRING(80); // Human-readable error

    (* Transaction write-out *)
    xWritePumpTransaction   : BOOL;    // One-cycle pulse to trigger DB write
    rFinalLitersForDB       : REAL;    // Latched final liters at stop (pre-reset)

    (* Flowmeter reset pulse after DB write *)
    xMeterReset             : BOOL;    // One-cycle pulse to reset external counter
END_VAR

VAR
    (*
        Internal state machine
        Using INT for portability; constants defined below.
    *)
    iState                  : INT;     // 0=Idle,1=WaitRFID,2=WaitLiters,3=WaitVehicle,4=Arming,5=StartFlowWait,6=Dispensing,7=Stopping,8=Write,9=MeterReset
    iNextState              : INT;

    (* Pushbutton edge/latch handling *)
    xPB_Last                : BOOL;    // Previous scan pushbutton
    xPumpLatched            : BOOL;    // Internal latch toggled by pushbutton rising edge

    (* Step timeout timer (per interactive step) *)
    tProcessTimeout         : TIME;    // TIME derived from usiProcessTimeout_s
    tonStepTimeout          : TON;

    (* Start-flow window: must see increase within 30s after approval *)
    tonStartFlow            : TON;     // PT= T#30S

    (* Stall detection: compare rBefore vs rAfter over 30s window while dispensing *)
    tonStallWindow          : TON;     // PT= T#30S
    rBeforeLCount           : REAL;    // Snapshot at start of stall window
    rAfterLCount            : REAL;    // Snapshot at end

    (* 1-second cadence for display/limit check updates while dispensing *)
    tonOneSecond            : TON;     // PT= T#1S

    (* Rising-edge detection for xRFIDPopupCheck *)
    xRFID_Last              : BOOL;

    (* Bookkeeping *)
    rPrevLiterCount         : REAL;    // For start-flow detection (did it increase at all?)
    xAnyDispensed           : BOOL;    // TRUE if rLiterCountIn >= 0.1 at stop
    xWritePulsed            : BOOL;    // Ensures single write pulse
    xResetPulsed            : BOOL;    // Ensures single meter reset pulse

    (* Small epsilon to treat miniscule jitter *)
    rEps                    : REAL := 0.001;
END_VAR

VAR CONSTANT
    STATE_Idle              : INT := 0;
    STATE_WaitRFID          : INT := 1;
    STATE_WaitLiters        : INT := 2;
    STATE_WaitVehicle       : INT := 3;
    STATE_Arming            : INT := 4;
    STATE_StartFlowWait     : INT := 5;
    STATE_Dispensing        : INT := 6;
    STATE_Stopping          : INT := 7;
    STATE_Write             : INT := 8;
    STATE_MeterReset        : INT := 9;

    (* Thresholds *)
    FLOW_START_WINDOW       : TIME := T#30S;
    FLOW_STALL_WINDOW       : TIME := T#30S;
    ONE_SECOND              : TIME := T#1S;
    MIN_COUNT_FOR_WRITE     : REAL := 0.1;   // rLiterCountIn >= 0.1 triggers DB write
    MIN_REQUEST_LITERS      : REAL := 1.0;   // rLitersRequested >= 1.0 to start
END_VAR

(* ------------------------- Initialization on first scan ------------------------- *)
IF NOT __INIT THEN
    // nothing special; rely on explicit reset in Idle
END_IF

(* Convert step timeout seconds to TIME each scan *)
tProcessTimeout := T#0S + TO_TIME(UDINT(usiProcessTimeout_s) * 1000);

(* Rising edge detect on pushbutton *)
IF (xPumpPushButton AND NOT xPB_Last) THEN
    // Toggle the internal latch
    xPumpLatched := NOT xPumpLatched;
END_IF;
xPB_Last := xPumpPushButton;

(* Latch RFID approval on rising edge of xRFIDPopupCheck *)
IF (xRFIDPopupCheck AND NOT xRFID_Last) THEN
    xRFIDCheckApproved := TRUE;
END_IF;
xRFID_Last := xRFIDPopupCheck;

(* Default outputs each scan (some overwritten by states) *)
xRequestLitersPopup := FALSE;
xRequestVehiclePopup := FALSE;
xPumpApproved := FALSE;
xWritePumpTransaction := FALSE;
xMeterReset := FALSE;
xActive := (iState <> STATE_Idle);
xBusy := (iState <> STATE_Idle) AND (iState <> STATE_Write) AND (iState <> STATE_MeterReset);
IF NOT xError THEN sError := ''; END_IF;

(* ------------------------------ State machine ------------------------------ *)
CASE iState OF

    STATE_Idle:
        sState := 'Idle';
        xError := FALSE;
        xRFIDCheckApproved := FALSE;
        xAnyDispensed := FALSE;
        xWritePulsed := FALSE;
        xResetPulsed := FALSE;

        // Reset requested liters in Idle only if pump not latched
        IF NOT xPumpLatched THEN
            // waiting for operator; do nothing
        END_IF;

        // If operator latches pump ON, begin with RFID
        IF xPumpLatched THEN
            // Start step timeout for RFID stage
            tonStepTimeout(IN := TRUE, PT := tProcessTimeout);
            tonStartFlow(IN := FALSE);
            tonStallWindow(IN := FALSE);
            tonOneSecond(IN := FALSE);

            rPrevLiterCount := rLiterCountIn; // baseline before any flow
            sState := 'WaitRFID';
            iState := STATE_WaitRFID;
        END_IF;

    STATE_WaitRFID:
        sState := 'WaitRFID';

        // Keep timeout running
        tonStepTimeout(IN := TRUE, PT := tProcessTimeout);

        // Abort conditions
        IF NOT xPumpLatched THEN
            sError := 'Cancelled by operator during RFID';
            xError := TRUE;
            iState := STATE_Stopping;
        ELSIF tonStepTimeout.Q THEN
            sError := 'Timeout waiting for RFID approval';
            xError := TRUE;
            iState := STATE_Stopping;
        ELSIF xRFIDCheckApproved THEN
            // RFID latched; move to liters entry
            tonStepTimeout(IN := FALSE); tonStepTimeout(IN := TRUE, PT := tProcessTimeout);
            xRequestLitersPopup := TRUE; // Ask HMI to open dialog
            sState := 'WaitLiters';
            iState := STATE_WaitLiters;
        END_IF;

    STATE_WaitLiters:
        sState := 'WaitLiters';

        // Keep timeout running for user entry
        tonStepTimeout(IN := TRUE, PT := tProcessTimeout);
        xRequestLitersPopup := TRUE; // Keep requesting until provided

        // Abort conditions
        IF NOT xPumpLatched THEN
            sError := 'Cancelled by operator during liters entry';
            xError := TRUE;
            iState := STATE_Stopping;
        ELSIF tonStepTimeout.Q THEN
            sError := 'Timeout waiting for liters entry';
            xError := TRUE;
            iState := STATE_Stopping;
        ELSIF rLitersRequested >= MIN_REQUEST_LITERS THEN
            // Proceed to vehicle selection
            tonStepTimeout(IN := FALSE); tonStepTimeout(IN := TRUE, PT := tProcessTimeout);
            xRequestVehiclePopup := TRUE;
            sState := 'WaitVehicle';
            iState := STATE_WaitVehicle;
        END_IF;

    STATE_WaitVehicle:
        sState := 'WaitVehicle';

        tonStepTimeout(IN := TRUE, PT := tProcessTimeout);
        xRequestVehiclePopup := TRUE;

        // Abort conditions
        IF NOT xPumpLatched THEN
            sError := 'Cancelled by operator during vehicle selection';
            xError := TRUE;
            iState := STATE_Stopping;
        ELSIF tonStepTimeout.Q THEN
            sError := 'Timeout waiting for vehicle approval';
            xError := TRUE;
            iState := STATE_Stopping;
        ELSIF xVehicleApproved THEN
            // All conditions met; arming
            tonStepTimeout(IN := FALSE);
            sState := 'Arming';
            iState := STATE_Arming;
        END_IF;

    STATE_Arming:
        sState := 'Arming';

        // Final gate check
        IF NOT xPumpLatched THEN
            sError := 'Cancelled by operator before start';
            xError := TRUE;
            iState := STATE_Stopping;
        ELSIF (NOT xRFIDCheckApproved) OR (NOT xVehicleApproved) OR (rLitersRequested < MIN_REQUEST_LITERS) THEN
            sError := 'Prestart conditions not met';
            xError := TRUE;
            iState := STATE_Stopping;
        ELSE
            // Begin start-flow window
            rPrevLiterCount := rLiterCountIn;
            tonStartFlow(IN := TRUE, PT := FLOW_START_WINDOW);

            sState := 'StartFlowWait';
            iState := STATE_StartFlowWait;
        END_IF;

    STATE_StartFlowWait:
        sState := 'StartFlowWait';

        // Assert pump approved to open valve/enable drive
        xPumpApproved := TRUE;

        // If operator cancels, stop
        IF NOT xPumpLatched THEN
            sError := 'Stopped by operator before flow';
            xError := TRUE;
            tonStartFlow(IN := FALSE);
            iState := STATE_Stopping;
        ELSE
            // Detect any increase within 30s
            IF (rLiterCountIn > (rPrevLiterCount + rEps)) THEN
                // Flow detected; enter dispensing
                tonStartFlow(IN := FALSE);
                tonOneSecond(IN := TRUE, PT := ONE_SECOND);
                // Initialize stall window
                rBeforeLCount := rLiterCountIn;
                tonStallWindow(IN := TRUE, PT := FLOW_STALL_WINDOW);
                sState := 'Dispensing';
                iState := STATE_Dispensing;
            ELSIF tonStartFlow.Q THEN
                // No flow within window => fault
                sError := 'No flow detected within 30s';
                xError := TRUE;
                tonStartFlow(IN := FALSE);
                iState := STATE_Stopping;
            END_IF;
        END_IF;

    STATE_Dispensing:
        sState := 'Dispensing';

        // Keep the pump running
        xPumpApproved := TRUE;

        // Mark that something was dispensed if we cross threshold
        IF (rLiterCountIn >= (MIN_COUNT_FOR_WRITE - rEps)) THEN
            xAnyDispensed := TRUE;
        END_IF;

        // 1-second cadence: UI refresh/limit check
        tonOneSecond(IN := TRUE, PT := ONE_SECOND);
        IF tonOneSecond.Q THEN
            tonOneSecond(IN := FALSE); // retrigger
            tonOneSecond(IN := TRUE, PT := ONE_SECOND);

            // Check if target reached: rLitersRequested <= rLiterCountIn
            IF (rLitersRequested <= (rLiterCountIn + rEps)) THEN
                sState := 'Stopping(Target reached)';
                iState := STATE_Stopping;
            END_IF;
        END_IF;

        // Operator stop at any time
        IF NOT xPumpLatched THEN
            sState := 'Stopping(Operator stop)';
            iState := STATE_Stopping;
        END_IF;

        // Stall detection: compare before vs after every 30s window
        tonStallWindow(IN := TRUE, PT := FLOW_STALL_WINDOW);
        IF tonStallWindow.Q THEN
            // End of window: take after snapshot and compare
            rAfterLCount := rLiterCountIn;
            IF (ABS(rAfterLCount - rBeforeLCount) <= rEps) THEN
                sError := 'Flow stalled for 30s';
                xError := TRUE;
                sState := 'Stopping(Stall)';
                iState := STATE_Stopping;
            ELSE
                // Reset window with new baseline
                rBeforeLCount := rLiterCountIn;
                tonStallWindow(IN := FALSE); // retrigger
                tonStallWindow(IN := TRUE, PT := FLOW_STALL_WINDOW);
            END_IF;
        END_IF;

    STATE_Stopping:
        sState := 'Stopping';

        // De-energize pump
        xPumpApproved := FALSE;

        // Latch final liters for DB
        rFinalLitersForDB := rLiterCountIn;

        // Decide whether to write
        IF (rFinalLitersForDB >= (MIN_COUNT_FOR_WRITE - rEps)) AND (NOT xWritePulsed) THEN
            xWritePumpTransaction := TRUE;  // one scan pulse
            xWritePulsed := TRUE;
            sState := 'Write';
            iState := STATE_Write;
        ELSE
            // No write, proceed to meter reset anyway (optional)
            sState := 'MeterReset';
            iState := STATE_MeterReset;
        END_IF;

        // Clear activity
        xPumpLatched := FALSE; // require a new press for next transaction

        // Stop timers
        tonStartFlow(IN := FALSE);
        tonStallWindow(IN := FALSE);
        tonOneSecond(IN := FALSE);
        tonStepTimeout(IN := FALSE);

    STATE_Write:
        sState := 'Write';

        // Assume external DB write completes synchronously or next scan
        // Immediately proceed to meter reset next scan
        sState := 'MeterReset';
        iState := STATE_MeterReset;

    STATE_MeterReset:
        sState := 'MeterReset';

        // Pulse meter reset exactly once after write stage
        IF NOT xResetPulsed THEN
            xMeterReset := TRUE;   // one-scan pulse
            xResetPulsed := TRUE;
        ELSE
            // Return to idle cleanly
            xError := FALSE;       // clear error for next run; keep sError for last-cycle visibility
            sError := sError;      // retain message one more scan (optional)
            sState := 'Idle';
            iState := STATE_Idle;

            // Clear latches for next cycle
            xRFIDCheckApproved := FALSE;
        END_IF;

ELSE
    // Failsafe to Idle on unknown state
    iState := STATE_Idle;
END_CASE;