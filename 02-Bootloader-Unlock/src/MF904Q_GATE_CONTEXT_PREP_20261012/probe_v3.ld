original_snprintf = 0x1e19d;
original_info = 0x19ced;
original_okay = 0x19ebd;
original_fail = 0x19d35;
original_constructor = 0x22ed1;
original_encrypt = 0x230d5;
lk_malloc = 0x1e1e9;
lk_free = 0x1e21d;
original_erase_commit = 0x1c4f1;
original_write = 0x23055;
config_resume = 0x22597;
original_gate = 0x2258d;
SECTIONS {
 . = 0x1c3dc; .diag : { *(.entry) *(.emit) *(.ctor) *(.done) *(.deny) *(.progress) *(.gate_read_support) }
 ASSERT(SIZEOF(.diag)<=276,"diagnostic overflow")
 . = 0x1c552; .hook_erase : { *(.hook_erase) }
 . = 0x1c654; .body : { *(.body) *(.gate_ctor_progress) }
 ASSERT(SIZEOF(.body)<=240,"body overflow")

 . = 0x22592; .hook_config : { *(.hook_config) }
 . = 0x2337a; .hook_crypto1 : { *(.hook_crypto1) }
 . = 0x233a6; .hook_write1 : { *(.hook_write1) }
 . = 0x233da; .hook_crypto2 : { *(.hook_crypto2) }
 . = 0x23406; .hook_gate : { *(.hook_gate) }
 . = 0x2340e; .hook_constructor : { *(.hook_constructor) }
 . = 0x23436; .hook_write2 : { *(.hook_write2) }
 . = 0x2922c; .hook_raw : { *(.hook_raw) }
 /DISCARD/ : { *(.ARM.attributes) *(.comment) *(.ARM.exidx*) *(.ARM.extab*) }
}
