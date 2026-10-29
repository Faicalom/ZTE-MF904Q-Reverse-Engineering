# Findings with explicit evidence levels

## Confirmed in saved device evidence

* Original DA1/DA2 executed and returned actual flash bytes on Windows.
* All23 GPT partitions, both boot regions and User were saved; historical independent verification PASS covered31 principal files.
* The final measured LK completed original unlock, followed by independent yes.
* Factory LK restoration passed full readback and independently returned yes after a new entry.
* Selected custom system sessions passed complete readback; WEB_ONLY contains factory LCD APK.

## Owner observations and recorded functional tests

* Android/network operation after unlock, including an actual Internet test.
* B operated normally for two days.
* Arabic LCD output and temporary Arabic WebUI success.
* Combined/WEB_ONLY/LCD_ONLY power-off; later off/on behavior also reported.
See CURRENT_BASELINE_20261023.md for the newly recovered B restore and later distinct factory restore; current physical state was not probed.

## Not established

Shutdown root cause, universal compatibility, guaranteed debrick, an external UART pinout, a fully isolated live LCD_ONLY web-stock state, complete dependency/legal clearance of the public tools, or a permanent stable Arabic ROM. See [open questions](OPEN_TECHNICAL_QUESTIONS.md).
