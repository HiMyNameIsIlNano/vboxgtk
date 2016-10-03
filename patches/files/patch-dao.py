--- vboxgtk/dao.py.orig	2012-10-26 10:32:16.000000000 +0200
+++ vboxgtk/dao.py	2016-10-03 14:07:05.194945000 +0200
@@ -198,7 +198,7 @@
 
 def create_vm(vm_name, os_type, hd_size, hd_dynamic):
     try:
-        vm = vbox.createMachine('', vm_name, os_type, None, False)
+        vm = vbox.createMachine('', vm_name, [], os_type, '')
         vm.addStorageController('IDE Controller', cts.StorageBus_IDE)
         ot = vbox.getGuestOSType(os_type)
         vm.memorySize = ot.recommendedRAM
@@ -210,15 +210,15 @@
         iface.msg_show(True, _("Could not create the VM"), str(e))
         return 1
     vms.append(vm)
-    vm_name_full = vbox.composeMachineFilename(vm_name, None)
+    vm_name_full = vbox.composeMachineFilename(vm_name, '', '', None)
     vm_dir = os.path.dirname(vm_name_full)
-    hd_path = os.path.join(vm_dir, '%s.img' % (vm_name,))
+    hd_path = os.path.join(vm_dir, '%s.vdi' % (vm_name,))
     err_msg = _("Could not create the VM hard disk")
     try:
-        hd = vbox.createHardDisk('', hd_path)
+        hd = vbox.createMedium('', hd_path, cts.AccessMode_ReadWrite, cts.DeviceType_HardDisk)
         mtype = (cts.MediumVariant_Standard if hd_dynamic
-                 else cts.MediumVariant_Fixed)
-        progress = hd.createBaseStorage(hd_size * 1024 * 1024, mtype)
+                 else cts.MediumVariant_Fixed) 
+        progress = hd.createBaseStorage(hd_size * 1024 * 1024, (mtype, ))
         progress.waitForCompletion(-1)
     except Exception as e:
         delete_vm(-1, False)
@@ -236,11 +236,11 @@
     close_session(vm)
     err_msg = _("Could not delete the VM")
     try:
-        media = vm.unregister(cts.CleanupMode_DetachAllReturnHardDisksOnly)
-        del vms[vm_number]
-        mediadel = media if delete_media else []
-        progress = vm.delete(mediadel)
-        progress.waitForCompletion(-1)
+		media = vm.unregister(cts.CleanupMode_DetachAllReturnHardDisksOnly)
+		del vms[vm_number]
+		mediadel = media if delete_media else []
+		progress = vm.deleteConfig(mediadel)
+		progress.waitForCompletion(-1)
     except Exception as e:
         iface.msg_show(True, err_msg, str(e))
         return 1
@@ -333,12 +333,14 @@
     if devtype == 'hd':
         port = 0
         dev_type = cts.DeviceType_HardDisk
+        dev_mode = cts.AccessMode_ReadWrite
         try:
-            device = vbox.findMedium(dev_id, dev_type)
+			device = vbox.openMedium(dev_id, dev_type, dev_mode, False) 	
         except Exception as e:
             iface.msg_show(True, _("Could not find hd"), str(e))
             return 1
     else:
+		# In case of DVDs the dev_id is None
         port = 1
         dev_type = cts.DeviceType_DVD
         device = util.find(dvd_host_drives, 'id', dev_id)
@@ -368,7 +370,7 @@
 def mount_dvd(vm_number, dvd_id):
     vm = vms[vm_number]
     try:
-        dvd = vbox.findMedium(dvd_id, cts.DeviceType_DVD) if dvd_id else None
+		dvd = vbox.openMedium(dvd_id, cts.DeviceType_DVD, cts.AccessMode_ReadOnly, False) if dvd_id else None
     except Exception as e:
         iface.msg_show(True, _("Could not find dvd"), str(e))
         return 1
@@ -496,4 +498,3 @@
     if check_progress_status(progress, err_msg):
         return 1
     return 0
-
