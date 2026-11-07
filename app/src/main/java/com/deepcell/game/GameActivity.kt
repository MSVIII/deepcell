package com.deepcell.game

import android.content.Intent
import android.graphics.drawable.AnimationDrawable
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.animation.AnimationUtils
import android.widget.FrameLayout
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.deepcell.game.data.GameDatabase
import com.deepcell.game.data.JsonLoader
import com.deepcell.game.model.Enemy
import com.deepcell.game.model.Floor
import com.deepcell.game.model.GameState
import com.deepcell.game.model.Survivor
import com.deepcell.game.model.Upgrade
import com.deepcell.game.model.Wave
import com.deepcell.game.ui.FloorAdapter
import com.deepcell.game.ui.Fx
import com.deepcell.game.ui.Notifier
import com.deepcell.game.ui.Sfx
import com.deepcell.game.ui.UpgradeAdapter
import kotlin.random.Random

/**
 * The main screen, top to bottom: sky (enemies fall), hatch + health bar,
 * underground floors, upgrade list, bottom tabs.
 *
 * One Handler loop runs every FRAME_MS while the screen is visible. It moves enemies,
 * spawns the wave, and once per second runs the automation machines.
 *
 * Save flow: onResume loads from SQLite and adds offline earnings; onPause stops the
 * loop and saves. Other screens (Survivors, Settings) write straight to SQLite.
 */
class GameActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_BUNKER_NAME = "bunker_name"
        const val EXTRA_NEW_GAME = "new_game"

        const val BASE_HATCH_HP = 100
        private const val HATCH_HP_PER_PLATING = 20
        private const val REPAIR_SCRAP_COST = 1
        private const val REPAIR_AMOUNT = 5

        private const val FRAME_MS = 33L                  // about 30 updates per second
        private const val AUTOMATION_TICK_MS = 1000L      // machines act once per second
        private const val WAVE_BREAK_MS = 2000L           // pause before the next wave
        private const val MAX_OFFLINE_SECONDS = 8 * 60 * 60L
        private const val MIN_OFFLINE_SECONDS_FOR_TOAST = 30L

        // Upgrade ids from assets/upgrades.json
        private const val UP_TAP_POWER = "tap_power"
        private const val UP_HATCH_PLATING = "hatch_plating"
        private const val UP_DIG_TOOLS = "dig_tools"
        private const val UP_FARM_TOOLS = "farm_tools"
        private const val AUTO_TURRET = "auto_turret"
        private const val DRILL_RIG = "drill_rig"

        // Roof guards: spots on the deck as fractions of the bunker image (left of the hatch,
        // right of it, then closer in), the deck height, and the guard frame size.
        private val GUARD_SLOTS = floatArrayOf(0.34f, 0.66f, 0.43f, 0.57f)
        private const val DECK_Y = 0.49f
        private const val GUARD_DP = 47
        private const val FEET_Y = 0.93f          // feet in the guard frame
        private const val GUARD_FIRE_MS = 230L
        private const val HATCH_Y = 0.30f         // hatch on the bunker image, for sparks
        // Enemy flight: side-to-side sway and up-down bob (sine waves, so they ease in and out
        // at each end of the swing).
        private const val SWAY_DP = 10f
        private const val BOB_DP = 3f
        private const val SWAY_SPEED = 2.2f

        /** Enemy HP multiplier for each entry of R.array.difficulty_names. */
        private val DIFFICULTY_HP = doubleArrayOf(0.75, 1.0, 1.5)
    }

    // ---- views ----
    private lateinit var sky: FrameLayout
    private lateinit var bunker: FrameLayout
    private lateinit var roofCrew: FrameLayout
    private lateinit var fxLayer: FrameLayout
    private lateinit var hatchBar: ProgressBar
    private lateinit var hatchText: TextView
    private lateinit var hudScrap: TextView
    private lateinit var hudFood: TextView
    private lateinit var hudWave: TextView
    private lateinit var hudBossIcon: ImageView
    private lateinit var upgradeSheet: LinearLayout
    private lateinit var upgradeTitle: TextView
    private lateinit var tabButtons: List<ImageButton>

    // ---- data ----
    private lateinit var db: GameDatabase
    private lateinit var sfx: Sfx
    private val guardViews = ArrayList<ImageView>()
    private lateinit var upgrades: List<Upgrade>
    private lateinit var waveData: JsonLoader.WaveData
    private lateinit var floorAdapter: FloorAdapter
    private lateinit var upgradeAdapter: UpgradeAdapter
    private var state: GameState? = null
    private var survivors: List<Survivor> = emptyList()
    private var difficultyHp = 1.0
    /** Upgrade type shown in the sheet, or null when the sheet is closed. */
    private var currentTab: String? = null

    private lateinit var digFloor: Floor
    private lateinit var farmFloor: Floor

    // ---- wave in progress ----
    private val enemies = ArrayList<Enemy>()
    private val spawnQueue = ArrayList<String>()
    private var currentWave: Wave? = null
    private var waveHpScale = 1.0
    private var spawnTimerMs = 0L
    private var automationTimerMs = 0L
    /** Goes up every time a wave (re)starts, so the loop can tell a breach happened mid-frame. */
    private var waveGeneration = 0

    // ---- Handler game loop (Module 6) ----
    private val handler = Handler(Looper.getMainLooper())
    private val gameLoop = object : Runnable {
        override fun run() {
            step()
            handler.postDelayed(this, FRAME_MS)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_game)

        db = GameDatabase(this)
        upgrades = JsonLoader.loadUpgrades(this)
        waveData = JsonLoader.loadWaves(this)
        Notifier.createChannel(this)

        sky = findViewById(R.id.sky)
        bunker = findViewById(R.id.bunker)
        roofCrew = findViewById(R.id.roofCrew)
        fxLayer = findViewById(R.id.fxLayer)
        sfx = Sfx(this)
        hatchBar = findViewById(R.id.hatchBar)
        hatchText = findViewById(R.id.hatchText)
        hudScrap = findViewById(R.id.hudScrap)
        hudFood = findViewById(R.id.hudFood)
        hudWave = findViewById(R.id.hudWave)
        hudBossIcon = findViewById(R.id.hudBossIcon)
        upgradeSheet = findViewById(R.id.upgradeSheet)
        upgradeTitle = findViewById(R.id.upgradeTitle)

        digFloor = Floor("dig", getString(R.string.floor_dig), "scrap", 10, 5)
        farmFloor = Floor("farm", getString(R.string.floor_farm), "food", 10, 3)
        floorAdapter = FloorAdapter(this, listOf(digFloor, farmFloor), { workersIn(it) }) { onFloorTapped(it) }
        val floorList = findViewById<ListView>(R.id.floorList)
        floorList.addFooterView(layoutInflater.inflate(R.layout.footer_bedrock, floorList, false), null, false)
        floorList.adapter = floorAdapter

        upgradeAdapter = UpgradeAdapter(this, { state }) { buyUpgrade(it) }
        findViewById<ListView>(R.id.upgradeList).adapter = upgradeAdapter
        findViewById<ImageButton>(R.id.upgradeClose).setOnClickListener { selectTab(null) }

        bunker.setOnClickListener { repairHatch() }

        // Bottom bar: three upgrade tabs and the Survivors screen.
        val defense = findViewById<ImageButton>(R.id.tabDefense)
        val supplies = findViewById<ImageButton>(R.id.tabSupplies)
        val automation = findViewById<ImageButton>(R.id.tabAutomation)
        tabButtons = listOf(defense, supplies, automation)
        defense.setOnClickListener { pop(it); selectTab(GameState.TYPE_DEFENSE) }
        supplies.setOnClickListener { pop(it); selectTab(GameState.TYPE_SUPPLIES) }
        automation.setOnClickListener { pop(it); selectTab(GameState.TYPE_AUTOMATION) }
        findViewById<ImageButton>(R.id.tabSurvivors).setOnClickListener {
            pop(it)
            val intent = Intent(this, SurvivorsActivity::class.java)
            intent.putExtra(SurvivorsActivity.EXTRA_BUNKER_NAME, state?.bunkerName)
            startActivity(intent)
        }
        findViewById<ImageButton>(R.id.settingsButton).setOnClickListener {
            val intent = Intent(this, SettingsActivity::class.java)
            intent.putExtra(SettingsActivity.EXTRA_BUNKER_NAME, state?.bunkerName)
            intent.putExtra(SettingsActivity.EXTRA_WAVE, state?.wave ?: 1)
            startActivity(intent)
        }

        // Extras from MainActivity (Module 7).
        val extras = intent.extras
        if (savedInstanceState == null && extras != null && extras.getBoolean(EXTRA_NEW_GAME, false)) {
            val name = extras.getString(EXTRA_BUNKER_NAME) ?: getString(R.string.default_bunker_name)
            Toast.makeText(this, getString(R.string.welcome, name), Toast.LENGTH_SHORT).show()
        }
        selectTab(null)
    }

    // ---------------- lifecycle (Module 5) ----------------

    override fun onResume() {
        super.onResume()
        val loaded = db.loadState()
        if (loaded == null) {           // save was reset or never made
            finish()
            return
        }
        state = loaded
        survivors = db.getSurvivors()
        sfx.enabled = db.getSetting(GameDatabase.SETTING_SOUND, "true") == "true"
        showRoofCrew()
        difficultyHp = DIFFICULTY_HP[db.getSetting(GameDatabase.SETTING_DIFFICULTY, "1").toInt()]

        digFloor.progress = loaded.digProgress
        farmFloor.progress = loaded.farmProgress
        digFloor.automated = loaded.level(DRILL_RIG) > 0
        farmFloor.automated = false     // Sprinkler / Auto-Harvester is on the roadmap

        addOfflineEarnings(loaded)

        if (currentWave == null) startWave()
        refreshAll()
        handler.post(gameLoop)
    }

    override fun onPause() {
        super.onPause()
        handler.removeCallbacks(gameLoop)
        saveNow()
    }

    override fun onDestroy() {
        handler.removeCallbacks(gameLoop)
        sfx.release()
        db.close()
        super.onDestroy()
    }

    private fun saveNow() {
        val s = state ?: return
        s.digProgress = digFloor.progress
        s.farmProgress = farmFloor.progress
        s.lastPlayed = System.currentTimeMillis()
        db.saveState(s)
    }

    /** Only automated rooms earn while the app is closed. Food has no machine yet. */
    private fun addOfflineEarnings(s: GameState) {
        val now = System.currentTimeMillis()
        val seconds = ((now - s.lastPlayed) / 1000L).coerceIn(0L, MAX_OFFLINE_SECONDS)
        s.lastPlayed = now
        val drillLevel = s.level(DRILL_RIG)
        if (drillLevel <= 0 || seconds <= 0) return

        val fills = digFloor.addProgress((seconds * drillLevel).toInt())
        val earned = fills * digFloor.yieldPerFill
        s.scrap += earned
        if (earned > 0 && seconds >= MIN_OFFLINE_SECONDS_FOR_TOAST) {
            Toast.makeText(this, getString(R.string.offline_earned, earned), Toast.LENGTH_LONG).show()
        }
    }

    // ---------------- game loop ----------------

    private fun step() {
        val s = state ?: return
        if (sky.height == 0) return     // layout not measured yet

        // Spawn the next enemy of the wave.
        val wave = currentWave
        val generation = waveGeneration
        spawnTimerMs += FRAME_MS
        if (wave != null && spawnQueue.isNotEmpty() && spawnTimerMs >= wave.spawnMs) {
            spawnTimerMs = 0
            spawnEnemy(spawnQueue.removeAt(0))
        }

        // Move enemies down. Anything that reaches the bottom of the sky hits the hatch.
        // enemy.y is the real position (it decides when the hatch is hit); the view adds a
        // flight sway on top, which never changes the timing.
        val pxPerDp = resources.displayMetrics.density
        val now = System.currentTimeMillis() / 1000f
        for (enemy in ArrayList(enemies)) {
            enemy.y += enemy.type.speedDp * pxPerDp * FRAME_MS / 1000f
            val fallen = (enemy.y / sky.height).coerceIn(0f, 1f)
            // Drift towards the bunker with ease-in-out (smoothstep): it turns slowly at the
            // start, crosses fastest in the middle, and lines up gently over the roof.
            val eased = fallen * fallen * (3f - 2f * fallen)
            val sway = Math.sin((now * SWAY_SPEED + enemy.phase).toDouble()).toFloat()
            val bob = Math.sin((now * SWAY_SPEED * 2f + enemy.phase).toDouble()).toFloat()
            // Sway fades out near the hatch so the hit point stays where the drift aims.
            val calm = 1f - eased
            enemy.view.translationX = enemy.startX + (enemy.targetX - enemy.startX) * eased +
                sway * SWAY_DP * pxPerDp * calm
            enemy.view.translationY = enemy.y + bob * BOB_DP * pxPerDp * calm
            if (enemy.y + enemy.view.height >= sky.height) {
                val blast = Math.max(enemy.view.width * 3 / 2, (64 * pxPerDp).toInt())
                Fx.burst(fxLayer, R.drawable.fx_explode, enemy.view.translationX + enemy.view.width / 2f,
                    sky.height.toFloat(), blast)
                sfx.play(Sfx.Sound.IMPACT)
                removeEnemy(enemy)
                damageHatch(enemy.type.damage)
                if (waveGeneration != generation) return   // a breach restarted the wave
            }
        }

        // Machines work once per second.
        automationTimerMs += FRAME_MS
        if (automationTimerMs >= AUTOMATION_TICK_MS) {
            automationTimerMs = 0
            automationTick(s)
        }

        if (wave != null && spawnQueue.isEmpty() && enemies.isEmpty()) onWaveCleared()
    }

    private fun automationTick(s: GameState) {
        // Auto-Turret: shoots the enemy closest to the hatch. Damage = its level.
        val turret = s.level(AUTO_TURRET)
        if (turret > 0) {
            val nearest = enemies.maxByOrNull { it.y }
            if (nearest != null) {
                sfx.play(Sfx.Sound.TURRET)
                hitEnemy(nearest, turret)
            }
        }
        // Drill Rig: fills Scrap Dig by itself. Progress per second = its level.
        val drill = s.level(DRILL_RIG)
        if (drill > 0) {
            val earned = digFloor.addProgress(drill) * digFloor.yieldPerFill
            s.scrap += earned
            digFloor.pendingPopup = earned
            floorAdapter.notifyDataSetChanged()
            refreshHud()
        }
    }

    // ---------------- waves and enemies ----------------

    /** Wave n uses entry (n-1) % 10 of waves.json. Each later 10-wave cycle adds HP. */
    private fun startWave() {
        val s = state ?: return
        val index = (s.wave - 1) % waveData.waves.size
        val cycle = (s.wave - 1) / waveData.waves.size
        val wave = waveData.waves[index]
        currentWave = wave
        waveGeneration++
        waveHpScale = (1.0 + cycle * waveData.hpScalePerCycle) * difficultyHp
        spawnQueue.clear()
        spawnQueue.addAll(wave.enemyIds)
        spawnTimerMs = -WAVE_BREAK_MS
    }

    private fun spawnEnemy(typeId: String) {
        val type = waveData.enemyTypes[typeId] ?: return
        val sizePx = (type.sizeDp * resources.displayMetrics.density).toInt()
        val view = ImageView(this)
        // Rotors spin / wings flap: rendered frames in an AnimationDrawable.
        Fx.loop(
            view, when (type.id) {
                "shrike" -> R.drawable.anim_shrike
                "bomber" -> R.drawable.anim_bomber
                "boss" -> R.drawable.anim_boss
                else -> R.drawable.anim_scout
            }
        )
        view.contentDescription = type.name
        view.layoutParams = FrameLayout.LayoutParams(sizePx, sizePx)
        val startX = Random.nextInt(0, (sky.width - sizePx).coerceAtLeast(1)).toFloat()
        // Aim somewhere over the bunker roof.
        val spread = bunker.width * 0.35f
        val targetX = sky.width / 2f - sizePx / 2f + Random.nextFloat() * 2 * spread - spread
        val hp = Math.max(1, Math.round(type.hp * waveHpScale).toInt())
        val enemy = Enemy(type, hp, -sizePx.toFloat(), startX, targetX, view, Random.nextFloat() * 6.28f)
        view.translationX = startX
        view.translationY = enemy.y
        view.setOnClickListener {
            guardsFire()
            sfx.play(Sfx.Sound.SHOT)
            hitEnemy(enemy, tapDamage())
        }
        sky.addView(view)
        view.startAnimation(AnimationUtils.loadAnimation(this, R.anim.enemy_in))
        enemies.add(enemy)
    }

    /** Manual shot: 1 + Sharpened Rounds level + one per survivor on the roof. */
    private fun tapDamage(): Int {
        val s = state ?: return 1
        return 1 + s.level(UP_TAP_POWER) + survivors.count { it.job == Survivor.JOB_ROOF }
    }

    private fun hitEnemy(enemy: Enemy, damage: Int) {
        val s = state ?: return
        if (!enemies.contains(enemy)) return
        enemy.hp -= damage
        enemy.view.startAnimation(AnimationUtils.loadAnimation(this, R.anim.hit_flash))
        val cx = enemy.view.translationX + enemy.view.width / 2f
        val cy = enemy.view.translationY + enemy.view.height / 2f
        if (enemy.hp <= 0) {
            Fx.burst(fxLayer, R.drawable.fx_explode, cx, cy, enemy.view.width * 2)
            sfx.play(Sfx.Sound.EXPLODE)
            removeEnemy(enemy)
            s.scrap += enemy.type.reward
            refreshHud()
            upgradeAdapter.notifyDataSetChanged()
        } else {
            Fx.burst(fxLayer, R.drawable.fx_sparks, cx, cy, enemy.view.width)
            sfx.play(Sfx.Sound.HIT)
        }
    }

    private fun removeEnemy(enemy: Enemy) {
        enemy.view.clearAnimation()
        sky.removeView(enemy.view)
        enemies.remove(enemy)
    }

    private fun clearSky() {
        for (enemy in ArrayList(enemies)) removeEnemy(enemy)
        spawnQueue.clear()
    }

    private fun onWaveCleared() {
        val s = state ?: return
        val cleared = s.wave
        s.wave += 1
        if (cleared % 10 == 0) {
            Notifier.show(
                this, Notifier.ID_BOSS_CLEARED,
                getString(R.string.notif_boss_title), getString(R.string.notif_boss_text, cleared)
            )
        }
        sfx.play(Sfx.Sound.WAVE)
        Toast.makeText(this, getString(R.string.wave_cleared, cleared), Toast.LENGTH_SHORT).show()
        startWave()
        saveNow()
        refreshHud()
    }

    // ---------------- hatch ----------------

    private fun maxHatchHp(): Int = BASE_HATCH_HP + HATCH_HP_PER_PLATING * (state?.level(UP_HATCH_PLATING) ?: 0)

    private fun damageHatch(amount: Int) {
        val s = state ?: return
        s.hatchHp = (s.hatchHp - amount).coerceAtLeast(0)
        bunker.startAnimation(AnimationUtils.loadAnimation(this, R.anim.hatch_shake))
        if (s.hatchHp == 0) onHatchBreached(s)
        refreshHud()
    }

    /** Breach rule: lose 25% of scrap, the hatch is patched, and the same wave repeats. */
    private fun onHatchBreached(s: GameState) {
        sfx.play(Sfx.Sound.ALARM)
        val lost = s.scrap / 4
        s.scrap -= lost
        s.hatchHp = maxHatchHp()
        clearSky()
        startWave()
        saveNow()
        Toast.makeText(this, getString(R.string.breach_toast, lost), Toast.LENGTH_LONG).show()
        Notifier.show(
            this, Notifier.ID_HATCH_BREACHED,
            getString(R.string.notif_breach_title), getString(R.string.notif_breach_text, s.wave, lost)
        )
        upgradeAdapter.notifyDataSetChanged()
    }

    /** Manual repair: tap the hatch. Costs scrap; the Repair Arm will automate this later. */
    private fun repairHatch() {
        val s = state ?: return
        when {
            s.hatchHp >= maxHatchHp() -> Toast.makeText(this, R.string.hatch_full, Toast.LENGTH_SHORT).show()
            s.scrap < REPAIR_SCRAP_COST -> Toast.makeText(this, R.string.not_enough_scrap, Toast.LENGTH_SHORT).show()
            else -> {
                s.scrap -= REPAIR_SCRAP_COST
                s.hatchHp = (s.hatchHp + REPAIR_AMOUNT).coerceAtMost(maxHatchHp())
                sfx.play(Sfx.Sound.REPAIR)
                Fx.burst(fxLayer, R.drawable.fx_sparks, bunker.left + bunker.width / 2f,
                    bunker.top + bunker.height * HATCH_Y, (48 * resources.displayMetrics.density).toInt())
                refreshHud()
            }
        }
    }

    // ---------------- floors and upgrades ----------------

    /** Manual dig/harvest: 1 + tools level + one per survivor working in that room. */
    private fun onFloorTapped(floor: Floor) {
        val s = state ?: return
        val isDig = floor === digFloor
        val tools = s.level(if (isDig) UP_DIG_TOOLS else UP_FARM_TOOLS)
        val workers = workersIn(floor)
        sfx.play(if (isDig) Sfx.Sound.DIG else Sfx.Sound.HARVEST, 0.92f + Random.nextFloat() * 0.16f)
        val fills = floor.addProgress(1 + tools + workers)
        val earned = fills * floor.yieldPerFill
        if (isDig) s.scrap += earned else s.food += earned
        floor.pendingPopup = earned
        floorAdapter.notifyDataSetChanged()
        refreshHud()
        if (fills > 0) upgradeAdapter.notifyDataSetChanged()
    }

    private fun buyUpgrade(upgrade: Upgrade) {
        val s = state ?: return
        val level = s.levelOf(upgrade)
        if (level >= upgrade.maxLevel) {
            Toast.makeText(this, R.string.already_maxed, Toast.LENGTH_SHORT).show()
            return
        }
        val cost = upgrade.costAt(level)
        if (s.scrap < cost) {
            Toast.makeText(this, R.string.not_enough_scrap, Toast.LENGTH_SHORT).show()
            return
        }
        s.scrap -= cost
        s.setLevel(upgrade, level + 1)
        sfx.play(Sfx.Sound.BUY)
        when (upgrade.id) {
            UP_HATCH_PLATING -> s.hatchHp += HATCH_HP_PER_PLATING
            DRILL_RIG -> digFloor.automated = true
        }
        saveNow()   // purchases are saved straight away
        Toast.makeText(this, getString(R.string.bought, upgrade.name, level + 1), Toast.LENGTH_SHORT).show()
        refreshAll()
    }

    /** Opens the upgrade sheet for a tab. Tapping the open tab again (or null) closes it. */
    private fun selectTab(type: String?) {
        if (::sfx.isInitialized && type != null) sfx.play(Sfx.Sound.TAP)
        currentTab = if (type == currentTab) null else type
        val types = listOf(GameState.TYPE_DEFENSE, GameState.TYPE_SUPPLIES, GameState.TYPE_AUTOMATION)
        tabButtons.forEachIndexed { i, button -> button.isSelected = types[i] == currentTab }
        val open = currentTab
        if (open == null) {
            if (upgradeSheet.visibility == View.VISIBLE) {
                // Ease out of view, then hide.
                val out = AnimationUtils.loadAnimation(this, R.anim.sheet_out)
                upgradeSheet.startAnimation(out)
            }
            upgradeSheet.visibility = View.GONE
            return
        }
        val wasOpen = upgradeSheet.visibility == View.VISIBLE
        val titles = mapOf(
            GameState.TYPE_DEFENSE to R.string.tab_defense,
            GameState.TYPE_SUPPLIES to R.string.tab_supplies,
            GameState.TYPE_AUTOMATION to R.string.tab_automation
        )
        upgradeTitle.setText(titles[open] ?: R.string.tab_defense)
        upgradeAdapter.show(upgrades.filter { it.type == open })
        upgradeSheet.visibility = View.VISIBLE
        if (!wasOpen) upgradeSheet.startAnimation(AnimationUtils.loadAnimation(this, R.anim.sheet_in))
    }

    /** Survivors working in a room. They are drawn in the room and add +1 per tap each. */
    private fun workersIn(floor: Floor): Int {
        val job = if (floor === digFloor) Survivor.JOB_DIG else Survivor.JOB_FARM
        return survivors.count { it.job == job }
    }

    /**
     * One guard on the bunker roof per survivor with the Roof job, up to 4. They stand on the
     * deck either side of the hatch, feet on the deck, aiming outwards (the frames aim right,
     * so guards left of the hatch are mirrored).
     */
    private fun showRoofCrew() {
        roofCrew.removeAllViews()
        guardViews.clear()
        val size = (GUARD_DP * resources.displayMetrics.density).toInt()
        val bunkerW = resources.getDimensionPixelSize(R.dimen.bunker_width)
        val bunkerH = resources.getDimensionPixelSize(R.dimen.bunker_height)
        val guards = Math.min(survivors.count { it.job == Survivor.JOB_ROOF }, GUARD_SLOTS.size)
        repeat(guards) {
            val slot = GUARD_SLOTS[it]
            val figure = ImageView(this)
            figure.layoutParams = FrameLayout.LayoutParams(size, size)
            figure.translationX = bunkerW * slot - size / 2f
            figure.translationY = bunkerH * DECK_Y - size * FEET_Y
            if (slot < 0.5f) figure.scaleX = -1f
            figure.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
            roofCrew.addView(figure)
            guardViews.add(figure)
            Fx.loop(figure, R.drawable.anim_guard_idle, it * 300L)
        }
    }

    /** Every roof guard plays one shot (muzzle flash in the frames), then goes back to idle. */
    private fun guardsFire() {
        for (guard in guardViews) {
            (guard.tag as? Runnable)?.let { guard.removeCallbacks(it) }
            guard.setImageResource(R.drawable.anim_guard_fire)
            (guard.drawable as? AnimationDrawable)?.start()
            val back = Runnable { Fx.loop(guard, R.drawable.anim_guard_idle) }
            guard.tag = back
            guard.postDelayed(back, GUARD_FIRE_MS)
        }
    }

    // ---------------- HUD ----------------

    private fun refreshAll() {
        refreshHud()
        floorAdapter.notifyDataSetChanged()
        upgradeAdapter.notifyDataSetChanged()
    }

    /** Pressed buttons squash and spring back. */
    private fun pop(view: View) {
        view.startAnimation(AnimationUtils.loadAnimation(this, R.anim.press_pop))
    }

    /** Sets a HUD number; when it goes up, it pops so the gain is noticed. */
    private fun setCount(view: TextView, value: Int) {
        val old = view.text.toString().toIntOrNull()
        view.text = value.toString()
        if (old != null && value > old) view.startAnimation(AnimationUtils.loadAnimation(this, R.anim.hud_pop))
    }

    private fun refreshHud() {
        val s = state ?: return
        setCount(hudScrap, s.scrap)
        setCount(hudFood, s.food)
        hudWave.text = getString(R.string.wave_number, s.wave)
        hudBossIcon.visibility = if (s.wave % 10 == 0) View.VISIBLE else View.GONE
        val max = maxHatchHp()
        hatchBar.max = max
        hatchBar.progress = s.hatchHp
        hatchText.text = getString(R.string.hatch_hp, s.bunkerName, s.hatchHp, max)
    }
}
