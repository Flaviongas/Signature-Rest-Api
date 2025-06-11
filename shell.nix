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


env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
	pkgs.stdenv.cc.cc.lib
		pkgs.libz
];
}
