#!/usr/bin/env python3

import re
from pathlib import Path

def find_line(code, pattern):
    for match in pattern.finditer(code):
        return code.count('\n', 0, match.start())


def replace_lines(file_path):
    seek_arg_declaration = re.compile(r"unw\*10")
    seek_nev_declaration = re.compile(r"nev=")
    seek_pflag_declaration = re.compile(r"Process generated")
    seek_format_declaration = re.compile(r"300  format")

    with open(file_path, "r") as f:
        code = f.read()
        lines = code.splitlines(keepends=True)
        arg_idx = find_line(code, seek_arg_declaration)
        nev_idx = find_line(code, seek_nev_declaration)
        pflag_idx = find_line(code, seek_pflag_declaration)
        format_idx = find_line(code, seek_format_declaration)


    if "arg*10" not in lines[arg_idx]:
        lines[arg_idx] = lines[arg_idx].rstrip("\n").rstrip() + ",arg*10\n"
    lines[nev_idx] = "\t\tCALL GET_COMMAND_ARGUMENT(1, arg)\n"
    lines[nev_idx + 1] = "\t\tREAD(arg, *) nev        ! no. of unweighted events generated to event record\n"
    lines[pflag_idx] = "\t\tCALL GET_COMMAND_ARGUMENT(2, pflag)    ! Process generated - see preamble for options\n"
    lines[format_idx] = " 300  format(i4,1x,i4,1x,i8,1x,i4,1x,i4,1x,i4,1x,i4,1x,E25.16,1x,\n"
    lines[format_idx + 1] = "     &E25.16,1x,E25.16,1x,E25.16,1x,E25.16,1x,E25.16,1x,E25.16)\n"
    lines[format_idx + 2] = " 301  format(i4,1x,i8,1x,i4,1x,i4,1x,i4,1x,i4,1x,i4,1x,E25.16,1x,E25.16\n"
    lines[format_idx + 3] = "     &,1x,E25.16,1x,E25.16,1x,E25.16,1x,E25.16,1x,E25.16,1x,E25.16,1x\n"
    lines[format_idx + 4] = "     &,E25.16)\n"

    new_code = "".join(lines)
    with open(file_path, "w") as f:
        f.write(new_code)


def main():
    dime_nonreson = Path(__file__).parent.parent.parent / "dimeMC" / "nonreson" / "dimemcv1.07.f"
    if not dime_nonreson.exists():
        print(f"Error: {dime_nonreson} does not exist.")
        print("Download it and save it to the folder dimeMC/nonreson")
        return
    dime_resonant = Path(__file__).parent.parent.parent / "dimeMC" / "resonant" / "dimemcv1.07_vsm.f"
    if not dime_resonant.exists():
        print(f"Error: {dime_resonant} does not exist.")
        print("Download it and save it to the folder dimeMC/resonant")
        return

    replace_lines(dime_nonreson)
    replace_lines(dime_resonant)


if __name__ == "__main__":
    main()