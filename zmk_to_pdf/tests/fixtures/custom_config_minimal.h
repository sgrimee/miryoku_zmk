#define MIRYOKU_LAYER_BASE \
&kp Q,    &kp W,    &kp E,    &kp R,    &kp T,    \
&kp Y,    &kp U,    &kp I,    &kp O,    &kp P,    \
\
&kp A,    &kp S,    &kp D,    &kp F,    &kp G,    \
&kp H,    &kp J,    &kp K,    &kp L,    &kp SQT,  \
\
&kp Z,    &kp X,    &kp C,    &kp V,    &kp B,    \
&kp N,    &kp M,    &kp COMMA, &kp DOT, &kp SLASH, \
\
U_NP,     U_NP,     U_LT(U_NAV, ESC), U_LT(U_NUM, SPACE), &kp TAB, \
&kp BSPC, &kp RET,  &kp DEL,  U_NP,     U_NP

#define MIRYOKU_LAYER_TAP \
&kp Q,    &kp W,    &kp E,    &kp R,    &kp T,    \
&kp Y,    &kp U,    &kp I,    &kp O,    &kp P,    \
\
&kp A,    &kp S,    &kp D,    &kp F,    &kp G,    \
&kp H,    &kp J,    &kp K,    &kp L,    &kp SQT,  \
\
&kp Z,    &kp X,    &kp C,    &kp V,    &kp B,    \
&kp N,    &kp M,    &kp COMMA, &kp DOT, &kp SLASH, \
\
U_NP,     U_NP,     &kp ESC,  &kp SPACE, &kp TAB, \
&kp BSPC, &kp RET,  &kp DEL,  U_NP,     U_NP

#define MIRYOKU_LAYER_NAV \
U_BOOT,   &u_to_U_TAP, U_NA, U_NA, U_NA, \
U_NA,     U_NA, U_NA, U_NA, U_NA, \
\
&kp LCTRL, &kp LALT, &kp LGUI, &kp LSHFT, U_NA, \
&kp LEFT,  &kp DOWN, &kp UP,   &kp RIGHT, U_NA, \
\
U_NA,     &kp RALT, U_NA, U_NA, U_NA, \
&kp HOME, &kp PG_DN, &kp PG_UP, &kp END, U_NA, \
\
U_NP,     U_NP,     U_NA,     U_NA,     U_NA, \
&kp BSPC, &kp RET,  &kp DEL,  U_NP,     U_NP

#define MIRYOKU_LAYER_NUM \
U_BOOT,   &u_to_U_TAP, U_NA, U_NA, U_NA, \
&kp LBKT, &kp N7, &kp N8, &kp N9, &kp RBKT, \
\
&kp LCTRL, &kp LALT, &kp LGUI, &kp LSHFT, U_NA, \
&kp SEMI,  &kp N4,   &kp N5,   &kp N6,    &kp EQUAL, \
\
U_NA,     U_NA,     U_NA,     U_NA,     U_NA, \
&kp GRAVE, &kp N1,   &kp N2,   &kp N3,   &kp BSLH, \
\
U_NP,     U_NP,     U_NA,     U_NA,     U_NA, \
&kp N0,   &kp DOT,  U_NA,     U_NP,     U_NP
