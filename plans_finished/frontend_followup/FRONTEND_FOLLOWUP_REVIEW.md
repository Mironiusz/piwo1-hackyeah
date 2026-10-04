# Review: Follow-up of the web frontend after the work of Kuba and Adrian

Document state: 2026-10-04, initiative cancelled by the user as absorbed by `frontend_app`, see the entry Cancellation of 2026-10-04, moved to `plans_finished/`

## Cancellation of 2026-10-04

The initiative holds its seed and `FRONTEND_FOLLOWUP_REPORT.md`; no shape interview was run, so no review existed before this entry. The user cancelled it on 2026-10-04, while cleaning up `plans/`, as absorbed by `frontend_app`. The agent first described R-1 and R-2 of the report as handled there, then checked the code and corrected that account before the user kept the decision:

- R-1: the rule of the pseudonym is fixed by O-27 of `plans_finished/frontend_app/FRONTEND_APP_REVIEW.md`; constant `PSEUDONYM_PATTERN` of `frontend/src/views/accountForm.ts` accepts the set of the contract. Its related points are not fixed: function `trimPseudonym` still uses `String.prototype.trim`, and the form checks no maximum length of a password.
- R-2 is not fixed: functions `toDeviceDay` and `startOfNextDay` of `frontend/src/state/ownVotes.ts` still count the day in the time zone of the device. The review of `frontend_app` records it as a known limitation, R-3 of its section Review.
- R-3 - R-7 were already open points of `frontend_app` or of other initiatives, as section 4 of the report says.

`frontend_app` was closed the same day without a `ready` verdict, and its entry Closure lists what of this report stays undone; nothing of it is carried by this initiative. The report stays a frozen record. The directory moves to `plans_finished/frontend_followup/`.
