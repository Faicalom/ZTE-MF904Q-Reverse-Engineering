# Third-party notices and scoped source distribution

Upstream: https://github.com/bkerler/mtkclient ; exact examined revision `cd25cf9c1ff6d36e82697ac2c798e69e9cfb78c3`. The following are the actual original header notices recovered from that revision. No vendor DA, firmware, or upstream runtime executable is bundled.

## mtkclient/Library/Port.py

```text
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2026 GPLv3 License
import os
```

Original git content SHA256: `26775f24853f2c1c14ee994e32a692972d7ac647afdce04b5091094f6a0fa751`.

## mtkclient/Library/mtk_preloader.py

```text
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2026 GPLv3 License
import os
```

Original git content SHA256: `a0e07938abc49ac1ef547071c6a152c003047cb2b24b6c268284a2c9bba39d68`.

## mtkclient/Library/Connection/seriallib.py

```text
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2025
import time
```

Original git content SHA256: `1b89fcc3589c65ac27b714e09c13b06ddbfc078739c669addfd27802e7ded4a5`.

## mtkclient/Library/Connection/usblib.py

```text
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2025 GPLv3 License
import logging
```

Original git content SHA256: `859a11d8d68b15261a4eff0832ecb6dbb913f240c6aca56426cabdc5aa168b2e`.

## mtkclient/Library/DA/legacy/dalegacy_lib.py

```text
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2025 GPLv3 License
import logging
```

Original git content SHA256: `68b469d954f2627baa2d2d5f40904f777f85cbb1831664b462898d1ec623068b`.

## mtkclient/Library/DA/legacy/dalegacy_flash_param.py

```text
from binascii import hexlify
from mtkclient.Library.gui_utils import structhelper_io
from mtkclient.config.mtk_config import MtkConfig
from struct import pack
```

Original git content SHA256: `3630acbbb97f8ed6f834e46e230024e97fb58cb6dd0d432bc9e3bdf2f5f85d16`.

## mtkclient/Library/DA/legacy/dalegacy_param.py

```text
class Cmd:
    # COMMANDS
    DOWNLOAD_BLOADER_CMD = b"\x51"
    NAND_BMT_REMARK_CMD = b"\x52"
```

Original git content SHA256: `1e35c6552ca4158339888d064a90426ad43feab3cfa7f3000faed3c559e9d131`.

## mtkclient/Library/DA/daconfig.py

```text
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2025 GPLv3 License
import logging
```

Original git content SHA256: `bb40fdd4661cbf45da209d1266c01ba4731a1f88bfb9111071c96b1bf66dd8d5`.

## Modifications and distribution boundaries

24 reviewed DA/adapted/integrated source components retain GPLv3 source terms with notices and complete license text. Project-original orchestration is identified as original even when distributed within that covered DA-program source scope.26 other reviewed files are project-specific utilities/coordinators or factual metadata; they receive no automatic repository-wide GPL license. The complete per-file map gives the evidence and uncertainty.

This is a source research aggregate, not a binary distribution or a newly runnable, fully licensed integrated executable product. For a future combined program, all linked components require compatible grants; an independently written module does not evade combined-work obligations merely by being in a separate file. Independent code here is published with owner permission but without a newly selected general reuse license. That remaining licensing choice must be resolved before advertising the whole project as fully open source or releasing an integrated executable.

The withheld probe_v3.S prevents rebuilding the winning full LK from this package. No derived LK binary is supplied and no corresponding-source completeness claim is made for such a binary. Vendor DA and private identity/runtime-reference data remain external, rights-restricted inputs. GPL does not grant rights in manufacturer inputs.
