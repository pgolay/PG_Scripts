        def msg_box():
            
            str = "Isolate error: No objects to hide!"
            title = "Isolate Error"
            icon = System.Windows.Forms.MessageBoxIcon.Hand
            buttons = System.Windows.Forms.MessageBoxButtons.OK
            default = System.Windows.Forms.MessageBoxDefaultButton.Button1
            Rhino.UI.Dialogs.ShowMessageBox(str, title, buttons,icon, default)