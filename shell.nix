{ pkgs ? import <nixpkgs> {} }:

(pkgs.buildFHSEnv {
  name = "py-env";
  targetPkgs = pkgs: with pkgs;
    [ python3
      stdenv.cc.cc
      gcc.cc
      glibc
      glib
      libGL
      zlib

      # Migrations
      dbmate
    ];
  runScript = "bash";
}).env
