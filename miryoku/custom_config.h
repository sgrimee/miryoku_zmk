#define MIRYOKU_LAYER_BASE \
&kp Q,             &kp W,             &kp E,             &kp R,             &kp T,             &kp Y,             &kp U,             &kp I,             &kp O,             &kp P,             \
U_MT(LCTRL, A),    U_MT(LALT, S),     U_MT(LGUI, D),     U_MT(LSHFT, F),    &kp G,             &kp H,             U_MT(LSHFT, J),    U_MT(RGUI, K),     U_MT(LALT, L),     U_MT(RCTRL, SQT),   \
U_LT(U_BUTTON, Z), U_MT(RALT, X),     &kp C,             &kp V,             &kp B,             &kp N,             &kp M,             &kp COMMA,         U_MT(RALT, DOT),   U_LT(U_BUTTON, SLASH),\
U_NP,              U_NP,              U_LT(U_FUN, ESC),  U_LT(U_NUM, SPACE), U_LT(U_NAV, TAB), U_LT(U_SYM, BSPC), U_LT(U_BUTTON, RET), U_LT(U_MEDIA, DEL), U_NP,           U_NP

#define MIRYOKU_LAYER_TAP \
&kp Q,             &kp W,             &kp E,             &kp R,             &kp T,             &kp Y,             &kp U,             &kp I,             &kp O,             &kp P,             \
&kp A,             &kp S,             &kp D,             &kp F,             &kp G,             &kp H,             &kp J,             &kp K,             &kp L,             &kp SQT,           \
&kp Z,             &kp X,             &kp C,             &kp V,             &kp B,             &kp N,             &kp M,             &kp COMMA,         &kp DOT,           &kp SLASH,         \
U_NP,              U_NP,              &kp ESC,           &kp SPACE,         &kp TAB,           &kp BSPC,          &kp RET,           &kp DEL,           U_NP,              U_NP

#define MIRYOKU_LAYER_BUTTON \
U_RDO,             U_UND,             U_PST,             U_CPY,             U_CUT,             U_CUT,             U_CPY,             U_PST,             U_UND,             U_RDO,             \
&kp LCTRL,         &kp LALT,          &kp LGUI,          &kp LSHFT,         U_CPY,             U_CPY,             &kp RSHFT,         &kp RGUI,          &kp LALT,          &kp RCTRL,         \
U_UND,             U_CUT,             U_CPY,             U_PST,             U_PST,             U_PST,             U_PST,             U_CPY,             U_CUT,             U_UND,             \
U_NP,              U_NP,              U_BTN3,            U_BTN1,            U_BTN2,            U_BTN2,            U_BTN1,            U_BTN3,            U_NP,              U_NP


#define MIRYOKU_LAYER_NAV \
U_BOOT,            &u_to_U_TAP,       &u_to_U_EXTRA,     &u_to_U_BASE,      U_NA,              U_CUT,           U_CPY,             U_PST,             U_UND,             U_RDO,      \
&kp LCTRL,         &kp LALT,          &kp LGUI,          &kp LSHFT,         U_NA,              U_CPY,           &kp LEFT,          &kp DOWN,          &kp UP,            &kp RIGHT,    \
U_NA,              &kp RALT,          &u_to_U_NUM,       &u_to_U_NAV,       U_NA,              U_PST,           &kp HOME,          &kp PG_DN,         &kp PG_UP,         &kp END,    \
U_NP,              U_NP,              U_NA,              U_NA,              U_NA,              &kp BSPC,        &kp RET,           &kp DEL,           U_NP,              U_NP

#define MIRYOKU_LAYER_MOUSE \
U_BOOT,            &u_to_U_TAP,       &u_to_U_EXTRA,     &u_to_U_BASE,      U_NA,              U_CUT,             U_CPY,             U_PST,             U_UND,             U_RDO,   \
&kp LCTRL,         &kp LALT,          &kp LGUI,          &kp LSHFT,         U_NA,              U_CPY,              U_MS_L,            U_MS_D,            U_MS_U,            U_MS_R,  \
U_NA,              &kp RALT,          &u_to_U_SYM,       &u_to_U_MOUSE,     U_NA,              U_PST,              U_WH_L,            U_WH_D,            U_WH_U,            U_WH_R,  \
U_NP,              U_NP,              U_NA,              U_NA,              U_NA,              U_BTN2,            U_BTN1,            U_BTN3,            U_NP,              U_NP

#define MIRYOKU_LAYER_MEDIA \
U_BOOT,            &u_to_U_TAP,       &u_to_U_EXTRA,     &u_to_U_BASE,      U_NA,              U_RGB_TOG,         U_RGB_EFF,         U_RGB_HUI,         U_RGB_SAI,         U_RGB_BRI,   \
&kp LCTRL,         &kp LALT,          &kp LGUI,          &kp LSHFT,         U_NA,              U_EP_TOG,          &kp C_PREV,        &kp C_VOL_DN,      &kp C_VOL_UP,      &kp C_NEXT,  \
U_NA,              &kp RALT,          &u_to_U_FUN,       &u_to_U_MEDIA,     U_NA,              &u_out_tog,        &u_bt_sel_0,       &u_bt_sel_1,       &u_bt_sel_2,       &u_bt_sel_3, \
U_NP,              U_NP,              U_NA,              U_NA,              U_NA,              &kp C_STOP,        &kp C_PP,          &kp C_MUTE,        U_NP,              U_NP

#define MIRYOKU_LAYER_NUM \
U_BOOT,            &u_to_U_TAP,       &u_to_U_EXTRA,     &u_to_U_BASE,      U_NA,             &kp LBKT,          &kp N7,            &kp N8,            &kp N9,            &kp RBKT,   \
&kp LCTRL,         &kp LALT,          &kp LGUI,          &kp LSHFT,         U_NA,             &kp SEMI,          &kp N4,            &kp N5,            &kp N6,            &kp EQUAL,  \
U_NA,              &u_to_U_NUM,       &u_to_U_NAV,       &kp RALT,          U_NA,             &kp GRAVE,         &kp N1,            &kp N2,            &kp N3,            &kp BSLH,   \
U_NP,              U_NP,              U_NA,              U_NA,              U_NA,             &kp N0,            &kp DOT,           U_NA,              U_NP,              U_NP

#define MIRYOKU_LAYER_SYM \
&kp LBRC,          &kp AMPS,          &kp ASTRK,         &kp LPAR,          &kp RBRC,          U_NA,              &u_to_U_BASE,      &u_to_U_EXTRA,     &u_to_U_TAP,       U_BOOT,            \
&kp COLON,         &kp DLLR,          &kp PRCNT,         &kp CARET,         &kp PLUS,          U_NA,              &kp RSHFT,         &kp RGUI,          &kp LALT,          &kp RCTRL,         \
&kp TILDE,         &kp EXCL,          &kp AT,            &kp HASH,          &kp PIPE,          U_NA,              &u_to_U_SYM,       &u_to_U_MOUSE,     &kp RALT,          U_NA,              \
U_NP,              U_NP,              &kp LPAR,          &kp RPAR,          &kp UNDER,         U_NA,              U_NA,              U_NA,              U_NP,              U_NP

#define MIRYOKU_LAYER_FUN \
U_BOOT,            &u_to_U_TAP,       &u_to_U_EXTRA,     &u_to_U_BASE,      U_NA,             &kp F12,           &kp F7,            &kp F8,            &kp F9,            &kp PSCRN,          \
&kp LCTRL,         &kp LALT,          &kp LGUI,          &kp LSHFT,         U_NA,             &kp F11,           &kp F4,            &kp F5,            &kp F6,            &kp SLCK,           \
U_NA,              &u_to_U_NUM,       &u_to_U_NAV,       &kp RALT,          U_NA,             &kp F10,           &kp F1,            &kp F2,            &kp F3,            &kp PAUSE_BREAK,    \
U_NA,              U_NA,              U_NA,              U_NP,              U_NP,             U_NP,              U_NP,              U_NP,              U_NP,              U_NP


#define MIRYOKU_CLIPBOARD_MAC

