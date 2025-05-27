{ pkgs ? import <nixpkgs> {} }:
# For nix-shell

pkgs.mkShell {
  packages = [
    (pkgs.python312.withPackages (ps: with ps; [
      pandas
      ]))
  ];
shellHook = ''
    uv run manage.py runserver
  '';

  LD_LIBRARY_PATH="${pkgs.libGL}/lib/:${pkgs.stdenv.cc.cc.lib}/lib/:${pkgs.glib.out}/lib/";
}
