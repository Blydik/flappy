[app]
title = Flappy
package.name = flappy
package.domain = org.blodik
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 1

# — настройки Android (проверенные версии для стабильной сборки) —
android.accept_sdk_license = True
android.archs = arm64-v8a
android.api = 33
android.minapi = 24
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
