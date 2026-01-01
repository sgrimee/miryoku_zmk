#define MIRYOKU_LAYER_BASE \
&kp A,    &kp B,    &kp C,    &kp D,    &kp E,    \
&kp F,    &kp G,    &kp H,    &kp I,    &kp J,    \
\
U_MT(LCTRL, K), U_MT(LALT, L), &kp M, &kp N, &kp O, \
&kp P,    &kp Q,    &kp R,    U_LT(U_NAV, S), U_LT(U_NUM, T), \
\
&kp U,    &kp V,    &kp W,    &kp X,    &kp Y,    \
&kp Z,    U_NA,     U_NA,     U_NA,     U_NA,     \
\
U_NP,     U_NP,     U_LT(U_FUN, SPACE), U_LT(U_SYM, BSPC), U_LT(U_BUTTON, RET), \
&kp DEL,  U_NA,     U_NA,     U_NP,     U_NP

#define MIRYOKU_LAYER_TAP \
&kp A,    &kp B,    &kp C,    &kp D,    &kp E,    \
&kp F,    &kp G,    &kp H,    &kp I,    &kp J,    \
\
&kp K,    &kp L,    &kp M,    &kp N,    &kp O,    \
&kp P,    &kp Q,    &kp R,    &kp S,    &kp T,    \
\
&kp U,    &kp V,    &kp W,    &kp X,    &kp Y,    \
&kp Z,    U_NA,     U_NA,     U_NA,     U_NA,     \
\
U_NP,     U_NP,     &kp SPACE, &kp BSPC, &kp RET, \
&kp DEL,  U_NA,     U_NA,     U_NP,     U_NP

#define MIRYOKU_LAYER_NAV \
U_BOOT,   &kp N1,   &kp N2,   &kp N3,   U_NA,     \
U_NA,     U_NA,     U_NA,     U_NA,     U_NA,     \
\
&kp LCTRL, &kp LALT, &kp LGUI, &kp LSHFT, U_NA, \
&kp LEFT,  &kp DOWN, &kp UP,   &kp RIGHT, U_NA, \
\
U_NA,     &kp RALT, U_NA,     U_NA,     U_NA,     \
&kp HOME, &kp PG_DN, &kp PG_UP, &kp END, U_NA, \
\
U_NP,     U_NP,     U_NA,     U_NA,     U_NA, \
&kp BSPC, &kp RET,  &kp DEL,  U_NP,     U_NP

#define MIRYOKU_LAYER_FUN \
U_BOOT,   &kp F1,   &kp F2,   &kp F3,   U_NA,     \
&kp F4,   &kp F5,   &kp F6,   &kp F7,   &kp F8,   \
\
&kp LCTRL, &kp LALT, &kp LGUI, &kp LSHFT, U_NA, \
&kp F9,    &kp F10,  &kp F11,  &kp F12,  U_NA, \
\
U_NA,     U_NA,     U_NA,     U_NA,     U_NA,     \
U_NA,     U_NA,     U_NA,     U_NA,     U_NA,     \
\
U_NP,     U_NP,     U_NA,     U_NA,     U_NA, \
U_NA,     U_NA,     U_NA,     U_NP,     U_NP

#define MIRYOKU_LAYER_SYM \
&kp EXCL, &kp AT,   &kp HASH, &kp DLLR, &kp PRCNT, \
&kp CARET, &kp AMPS, &kp ASTRK, &kp LPAR, &kp RPAR, \
\
&kp LBRC, &kp RBRC, &kp LBKT, &kp RBKT, &kp LPAR, \
&kp RPAR, &kp SEMI, &kp COLON, &kp PLUS, &kp EQUAL, \
\
&kp MINUS, &kp UNDER, &kp PIPE, &kp BSLH, &kp SLASH, \
&kp DOT,  &kp COMMA, &kp TILDE, &kp GRAVE, &kp CARET, \
\
U_NP,     U_NP,     U_NA,     U_NA,     U_NA, \
U_NA,     U_NA,     U_NA,     U_NP,     U_NP
