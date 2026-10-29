# Extraction experiment history

| Stage | Observation | What changed / was learned | Limit |
|---|---|---|---|
| Earlier backup controller | BLOCKED; zero firmware files | driver repaired; READY banner received | not a successful extraction tool |
| Driver installation | VCOM 3.0.1504.0, Windows ProblemCode0 | Preloader port accessible | COM health did not complete handshake |
| Banner/handshake investigation | READY and incomplete complement exchange | separate unsolicited READY from command responses; avoid repeated A0 per banner character | cause of every prior byte mismatch not proved |
| Bounded protocol review | A0/0A/50/05 with matching complements | replay and parser work before live retry | local tests not a flash read |
| 9 October, session 20261009_104835_647022 | DA2_FIRST_SECTORS_READ | original DA stages, 34 sectors, real geometry | backup GPT and full partitions not yet read at this stage |
| Stock backup pipeline | seven firmware partitions, two boot areas and GPT | bounded range checks and checkpoints | non-private scope not a full User backup |
| Explicit private scope | sixteen other partitions and full User saved | separate identity-bound approval and encryption | raw material must remain private |
| Independent final verification, 9 October 12:15:27 +01 | PASS, 31 principal files, all partition/User comparisons | complete verified readable backup | RPMB/EXT_CSD and recovery from destroyed Preloader unproved |

The table records proven milestones rather than fabricating terminal commands for every intermediate experiment. See the complete guide for missing-command annotations and the source provenance register for reviewed records.
