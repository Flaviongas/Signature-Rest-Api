{ pkgs ? import <nixpkgs> {} }:
# For nix-shell

pkgs.mkShell {
  packages = [
    (pkgs.python312.withPackages (ps: with ps; [
      djangorestframework
      pandas
      django-filter
      requests
      django-cors-headers
      shortuuid
      django
      ]))
  ];
shellHook = ''
    # source back/bin/activate
    python manage.py runserver
  '';

  # LD_LIBRARY_PATH="${pkgs.libGL}/lib/:${pkgs.stdenv.cc.cc.lib}/lib/:${pkgs.glib.out}/lib/";
}
