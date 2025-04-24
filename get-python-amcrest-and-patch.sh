#!/bin/sh

DESTINATION="src/amcrest"
SHA="3c3fa5855b24a3692ae3bd3a9a335f81cecc999c"

TMP_DIR=$(mktemp -d)

git clone "https://github.com/tchellomello/python-amcrest.git" "$TMP_DIR"
(cd "$TMP_DIR" && git reset --hard "$SHA")

cat <<EOF | (cd "$TMP_DIR" && git apply)
diff --git a/src/amcrest/media.py b/src/amcrest/media.py
index e297a8f..f242f2d 100644
--- a/src/amcrest/media.py
+++ b/src/amcrest/media.py
@@ -26,13 +26,13 @@ class Media(Http):
 
     def factory_close(self, factory_id: str) -> str:
         ret = self.command(
-            f"mediaFileFind.cgi?action=factory.close&object={factory_id}"
+            f"mediaFileFind.cgi?action=close&object={factory_id}"
         )
         return ret.content.decode()
 
     def factory_destroy(self, factory_id: str) -> str:
         ret = self.command(
-            f"mediaFileFind.cgi?action=factory.destroy&object={factory_id}"
+            f"mediaFileFind.cgi?action=destroy&object={factory_id}"
         )
         return ret.content.decode()

EOF

rm -rf "$DESTINATION"
mv "$TMP_DIR/src/amcrest" "$DESTINATION"
rm -rf "$TMP_DIR"
