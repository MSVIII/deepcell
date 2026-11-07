"""Deepcell: shapes, selectors, animations and dimens.

Run from anywhere: python tools/art/gen_ui.py
Overwrites the files it generates in app/src/main/res.
"""
import os, sys
R = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "src", "main")
NS = 'xmlns:android="http://schemas.android.com/apk/res/android"'

def w(rel, text):
    p = os.path.join(R, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.strip() + "\n")

w("res/drawable/bg_sky.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Storm sky: dark at the top, dusty orange near the horizon, with a glow from the solar storm. -->
<layer-list {NS}>
    <item>
        <shape android:shape="rectangle">
            <gradient android:angle="270" android:startColor="@color/sky_top" android:centerColor="@color/sky_mid" android:endColor="@color/sky_bottom" />
        </shape>
    </item>
    <item>
        <shape android:shape="rectangle">
            <gradient android:type="radial" android:centerX="0.8" android:centerY="0.25" android:gradientRadius="220dp"
                android:startColor="#40E3A23B" android:endColor="#00E3A23B" />
        </shape>
    </item>
</layer-list>''')

w("res/drawable/bg_hud.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<layer-list {NS}>
    <item><shape><solid android:color="@color/amber_dark" /></shape></item>
    <item android:bottom="2dp"><shape><solid android:color="@color/soot" /></shape></item>
</layer-list>''')

w("res/drawable/bg_chip.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Resource counter in the HUD. -->
<shape {NS} android:shape="rectangle">
    <solid android:color="@color/panel" />
    <stroke android:width="1dp" android:color="@color/panel_line" />
    <corners android:radius="14dp" />
</shape>''')

w("res/drawable/bg_wave_badge.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<shape {NS} android:shape="rectangle">
    <solid android:color="@color/rust_dark" />
    <stroke android:width="1dp" android:color="@color/rust" />
    <corners android:radius="14dp" />
</shape>''')

def plate(fill, edge, radius="6dp", pressed=False):
    top = "1dp" if pressed else "0dp"
    bottom = "1dp" if pressed else "4dp"
    return f'''<layer-list>
            <item android:top="{top}"><shape><solid android:color="{edge}" /><corners android:radius="{radius}" /></shape></item>
            <item android:top="{top}" android:bottom="{bottom}"><shape><solid android:color="{fill}" /><corners android:radius="{radius}" /></shape></item>
        </layer-list>'''

w("res/drawable/bg_button.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Main button: an amber metal plate with a darker lower edge. Presses down when tapped. -->
<selector {NS}>
    <item android:state_enabled="false">
        {plate("@color/steel_dark", "#FF3E3C38")}
    </item>
    <item android:state_pressed="true">
        {plate("@color/amber_dark", "#FF6E4A14", pressed=True)}
    </item>
    <item>
        {plate("@color/amber", "@color/amber_dark")}
    </item>
</selector>''')

w("res/drawable/bg_button_dark.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Secondary button: a steel plate. -->
<selector {NS}>
    <item android:state_enabled="false">
        {plate("#FF34322E", "#FF26241F")}
    </item>
    <item android:state_pressed="true">
        {plate("@color/steel_dark", "#FF2A2824", pressed=True)}
    </item>
    <item>
        {plate("#FF4A4741", "#FF2A2824")}
    </item>
</selector>''')

w("res/drawable/bg_button_danger.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<selector {NS}>
    <item android:state_enabled="false">
        {plate("#FF34322E", "#FF26241F")}
    </item>
    <item android:state_pressed="true">
        {plate("#FF9A2A20", "#FF601A14", pressed=True)}
    </item>
    <item>
        {plate("@color/alarm_red", "#FF801F18")}
    </item>
</selector>''')

w("res/drawable/bg_panel.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Card / sheet background. -->
<layer-list {NS}>
    <item><shape><solid android:color="@color/panel_line" /><corners android:radius="10dp" /></shape></item>
    <item android:left="1dp" android:top="1dp" android:right="1dp" android:bottom="1dp">
        <shape><solid android:color="@color/panel" /><corners android:radius="9dp" /></shape>
    </item>
</layer-list>''')

w("res/drawable/bg_sheet.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Upgrade sheet that slides over the rooms: amber top edge, rounded top corners. -->
<layer-list {NS}>
    <item>
        <shape><solid android:color="@color/amber_dark" />
            <corners android:topLeftRadius="16dp" android:topRightRadius="16dp" /></shape>
    </item>
    <item android:top="2dp">
        <shape><solid android:color="@color/panel" />
            <corners android:topLeftRadius="15dp" android:topRightRadius="15dp" /></shape>
    </item>
</layer-list>''')

w("res/drawable/bg_field.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<shape {NS} android:shape="rectangle">
    <solid android:color="#CC15130F" />
    <stroke android:width="2dp" android:color="@color/panel_line" />
    <corners android:radius="8dp" />
    <padding android:left="14dp" android:right="14dp" android:top="10dp" android:bottom="10dp" />
</shape>''')

w("res/drawable/bg_plaque.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Floor number plate in the lift shaft. -->
<layer-list {NS}>
    <item><shape><solid android:color="@color/amber_dark" /><corners android:radius="5dp" /></shape></item>
    <item android:bottom="2dp"><shape><solid android:color="@color/amber" /><corners android:radius="5dp" /></shape></item>
</layer-list>''')

w("res/drawable/bg_label.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Small dark label stuck on a room wall. -->
<shape {NS} android:shape="rectangle">
    <solid android:color="#B315130F" />
    <corners android:radius="4dp" />
</shape>''')

w("res/drawable/bg_icon_slot.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<shape {NS} android:shape="rectangle">
    <solid android:color="@color/soot" />
    <stroke android:width="1dp" android:color="@color/panel_line" />
    <corners android:radius="8dp" />
</shape>''')

w("res/drawable/bg_bedrock.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Earth behind the rooms with the lift shaft running down the left side. -->
<layer-list {NS}>
    <item><shape><solid android:color="@color/earth" /></shape></item>
    <item android:gravity="left|fill_vertical" android:width="@dimen/shaft_width">
        <shape><solid android:color="@color/shaft" /></shape>
    </item>
    <item android:gravity="left|fill_vertical" android:left="10dp" android:width="3dp">
        <shape><solid android:color="@color/steel_dark" /></shape>
    </item>
    <item android:gravity="left|fill_vertical" android:left="43dp" android:width="3dp">
        <shape><solid android:color="@color/steel_dark" /></shape>
    </item>
</layer-list>''')

w("res/drawable/bg_room_frame.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Concrete slab above and below each room. -->
<layer-list {NS}>
    <item><shape><solid android:color="@color/slab" /></shape></item>
    <item android:top="6dp" android:bottom="4dp"><shape><solid android:color="@android:color/transparent" /></shape></item>
</layer-list>''')

w("res/drawable/bg_tab.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Bottom tab: amber line on top when selected, darker while pressed. -->
<selector {NS}>
    <item android:state_pressed="true">
        <shape><solid android:color="@color/panel_line" /></shape>
    </item>
    <item android:state_selected="true">
        <layer-list>
            <item><shape><solid android:color="@color/panel" /></shape></item>
            <item android:gravity="top" android:height="3dp"><shape><solid android:color="@color/amber" /></shape></item>
        </layer-list>
    </item>
    <item>
        <shape><solid android:color="@color/soot" /></shape>
    </item>
</selector>''')

def bar(name, color, back="@color/steel_dark", radius="4dp"):
    w(f"res/drawable/{name}.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<layer-list {NS}>
    <item android:id="@android:id/background">
        <shape><corners android:radius="{radius}" /><solid android:color="{back}" /></shape>
    </item>
    <item android:id="@android:id/progress">
        <clip><shape><corners android:radius="{radius}" /><solid android:color="{color}" /></shape></clip>
    </item>
</layer-list>''')
bar("progress_hatch", "@color/alarm_red", back="#CC15130F")
bar("progress_floor", "@color/amber", back="#B315130F", radius="3dp")
bar("progress_level", "@color/toxic_green", back="@color/soot", radius="2dp")

# animations
w("res/anim/work_bob.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Workers hop once when the room is tapped. -->
<translate {NS}
    android:duration="140"
    android:fromYDelta="0"
    android:toYDelta="-6dp"
    android:repeatCount="1"
    android:repeatMode="reverse" />''')
w("res/anim/float_up.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- "+5" payout text rises and fades. -->
<set {NS} android:fillAfter="true">
    <translate android:duration="700" android:fromYDelta="0" android:toYDelta="-36dp" />
    <alpha android:duration="700" android:startOffset="250" android:fromAlpha="1.0" android:toAlpha="0.0" />
</set>''')
w("res/anim/antenna_blink.xml", f'''<?xml version="1.0" encoding="utf-8"?>
<!-- Slow pulse for the title-screen emblem. -->
<alpha {NS}
    android:duration="1600"
    android:fromAlpha="1.0"
    android:toAlpha="0.75"
    android:repeatCount="infinite"
    android:repeatMode="reverse" />''')

w("res/values/dimens.xml", '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <dimen name="shaft_width">56dp</dimen>
    <dimen name="room_height">140dp</dimen>
    <dimen name="bunker_width">220dp</dimen>
    <dimen name="bunker_height">110dp</dimen>
</resources>''')
print("ui ok")
