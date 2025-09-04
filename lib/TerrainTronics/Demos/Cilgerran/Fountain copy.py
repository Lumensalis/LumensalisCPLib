from LumensalisCP.Simple import * # http://lumensalis.com/ql/h2Start

#############################################################################
main = ProjectManager(  "HammerFountain", useWifi=True)

stopped = main.addScene()  # scene active when wheel is "stopped"
spinning = main.addScene()  # scene active when wheel is "spinning"

# using a Cilgerran Castle board.  Take note of all the details
# you have to provide about which type of controller you're using, 
# what pins the Castle board is connected to, how many
# Cilgerran channels you want to use as LEDs, whether you
# want to enable the motor controller or battery monitor support...
cilgerran = main.TerrainTronics.addCilgerran()

fountainWheel  = cilgerran.motor

# set up the "UI" - everything here (as well as the ability to switch
# scenes) will automatically show up in the WebUI provided by LCPF
ui = main.panel
fountainSpeed = ui.addZeroToOne("water wheel rotation speed")
ui.monitorFloat( cilgerran.batteryMonitor ).displayName = "Battery Voltage"

# Now everything is in place so we can tell it _what_ we want the
# project to do.  Not _how_ to do it - LCPF takes care of that for you.

# when we "change" to spinning, enable override
spinning.setOnEnter( fountainWheel.manualOverride, True  )

# while we are in the spinning scene, set the motor speed from the fountainSpeed control
spinning.addRule(fountainWheel.manualSpeed, fountainSpeed )

# when we "leave" to spinning scene, stop the motor
spinning.setOnExit( fountainWheel.manualSpeed, 0 )
spinning.setOnExit( fountainWheel.manualOverride, False  )

# 3, 2, 1, IGNITION
main.launchProject( globals() )