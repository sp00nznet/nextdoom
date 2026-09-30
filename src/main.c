/* NeXTDoom 1.2 recomp: map Doom.app/Doom and its shlibs, enter crt0. */
#include "ns_runtime.h"

int main(int argc, char **argv) {
    ns_run(NEXTDOOM_ROOT "/Doom.app/Doom", NEXTDOOM_ROOT "/shlib", NEXTDOOM_ROOT, argc, argv);
    return 0;
}
