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
import com.deepcell.game.ui.Quality
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
        private const val FRAME_MS_LOW = 50L              // 20 updates per second in low detail
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
        private const val COLLECTOR = "collector"
        private const val STORAGE = "storage"

        // Rooms: each worker adds this much progress per second by themselves; storage holds
        // ten full bars, plus STORAGE_PER_LEVEL per Storage Racks level.
        private const val WORKER_RATE = 1
        private const val STORAGE_BARS = 10
        private const val STORAGE_PER_LEVEL = 25
        // Collector walking speed in dp per second: base, plus per level after the first.
        private const val COLLECTOR_SPEED_DP = 70f
        private const val COLLECTOR_SPEED_PER_LEVEL = 25f
        private const val COLLECTOR_GRAB_MS = 480L

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
    private lateinit var floorList: ListView
    /** Low detail (ui/Quality): fewer decorations, 20 updates a second. */
    private var lowDetail = false
    private var frameMs = FRAME_MS
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
            handler.postDelayed(this, frameMs)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_game)
        volumeControlStream = android.media.AudioManager.STREAM_MUSIC   // volume keys change game sounds

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
        floorList = findViewById(R.id.floorList)
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
        lowDetail = Quality.lowDetail(this, db.getSetting(GameDatabase.SETTING_DETAIL, Quality.AUTO))
        floorAdapter.lowDetail = lowDetail
        frameMs = if (lowDetail) FRAME_MS_LOW else FRAME_MS
        showRoofCrew()
        difficultyHp = DIFFICULTY_HP[db.getSetting(GameDatabase.SETTING_DIFFICULTY, "1").toInt()]

        digFloor.progress = loaded.digProgress
        farmFloor.progress = loaded.farmProgress
        digFloor.stock = loaded.digStock
        farmFloor.stock = loaded.farmStock
        updateCapacity(loaded)
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
        cancelCollector()
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
        s.digStock = digFloor.stock
        s.farmStock = farmFloor.stock
        s.lastPlayed = System.currentTimeMillis()
        db.saveState(s)
    }

    /**
     * While the app was closed the workers and the Drill Rig kept working. Without a Collector
     * their output waits in the rooms (up to the storage capacity); with one, it was carried up
     * as it was made, so storage never filled.
     */
    private fun addOfflineEarnings(s: GameState) {
        val now = System.currentTimeMillis()
        val seconds = ((now - s.lastPlayed) / 1000L).coerceIn(0L, MAX_OFFLINE_SECONDS)
        s.lastPlayed = now
        if (seconds <= 0) return
        val collector = s.level(COLLECTOR) > 0
        var scrap = 0
        var food = 0
        for (floor in listOf(digFloor, farmFloor)) {
            val amount = (productionPerSecond(floor, s) * seconds).toInt()
            if (amount <= 0) continue
            val made = if (collector) {
                floor.addProgress(amount) * floor.yieldPerFill
            } else {
                floor.work(amount)
            }
            if (floor === digFloor) scrap += made else food += made
        }
        if (collector) {
            s.scrap += scrap + digFloor.takeStock()
            s.food += food + farmFloor.takeStock()
        }
        if ((scrap > 0 || food > 0) && seconds >= MIN_OFFLINE_SECONDS_FOR_TOAST) {
            val text = if (collector) getString(R.string.collected, scrap, food)
            else getString(R.string.offline_stored, scrap, food)
            Toast.makeText(this, text, Toast.LENGTH_LONG).show()
        }
    }

    /** Progress per second a room makes by itself: its workers, plus the Drill Rig in Scrap Dig. */
    private fun productionPerSecond(floor: Floor, s: GameState): Int {
        val machine = if (floor === digFloor) s.level(DRILL_RIG) else 0
        return workersIn(floor) * WORKER_RATE + machine
    }

    /** Storage: ten full bars per room, more with Storage Racks. */
    private fun updateCapacity(s: GameState) {
        for (floor in listOf(digFloor, farmFloor)) {
            floor.capacity = floor.yieldPerFill * STORAGE_BARS + STORAGE_PER_LEVEL * s.level(STORAGE)
        }
    }

    // ---------------- game loop ----------------

    private fun step() {
        val s = state ?: return
        if (sky.height == 0) return     // layout not measured yet

        // Spawn the next enemy of the wave.
        val wave = currentWave
        val generation = waveGeneration
        spawnTimerMs += frameMs
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
            enemy.y += enemy.type.speedDp * pxPerDp * frameMs / 1000f
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

        updateCollector()

        // Machines work once per second.
        automationTimerMs += frameMs
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
        // Rooms work by themselves (workers, Drill Rig); the output goes into their storage.
        var changed = false
        for (floor in listOf(digFloor, farmFloor)) {
            val rate = productionPerSecond(floor, s)
            if (rate > 0 && !floor.isFull) {
                floor.work(rate)
                changed = true
            }
        }
        if (changed) floorAdapter.refresh(floorList)
        // Collector: walks to the next room that has something stored.
        if (s.level(COLLECTOR) > 0 && trip == null) startCollectorTrip(s)
    }

    // ---------------- collector ----------------

    /** One Collector trip through a room: walk in, grab, walk out. Driven by the game loop. */
    private class Trip(val floor: Floor, val index: Int, val walkMs: Long) {
        var phase = 0
        var phaseStart = System.currentTimeMillis()
    }

    private var trip: Trip? = null
    private var collectorNext = 0

    /** Sends the Collector to the next room (in order) with something in storage. */
    private fun startCollectorTrip(s: GameState) {
        val floors = listOf(digFloor, farmFloor)
        val index = (0 until floors.size).map { (collectorNext + it) % floors.size }
            .firstOrNull { floors[it].stock > 0 } ?: return
        collectorNext = index + 1
        val speed = (COLLECTOR_SPEED_DP + COLLECTOR_SPEED_PER_LEVEL * (s.level(COLLECTOR) - 1)) *
            resources.displayMetrics.density
        val walkMs = (floorAdapter.collectorDistancePx() / speed * 1000).toLong().coerceAtLeast(400L)
        trip = Trip(floors[index], index, walkMs)
    }

    /** Called every frame: moves the trip on and draws the Collector in its room. */
    private fun updateCollector() {
        val t = trip ?: return
        val now = System.currentTimeMillis()
        val elapsed = now - t.phaseStart
        when (t.phase) {
            0 -> if (elapsed >= t.walkMs) { t.phase = 1; t.phaseStart = now }
            1 -> if (elapsed >= COLLECTOR_GRAB_MS) { collectFrom(t.floor); t.phase = 2; t.phaseStart = now }
            2 -> if (elapsed >= t.walkMs) { t.phase = 3 }
        }
        val list = findViewById<ListView>(R.id.floorList)
        val row = list.getChildAt(t.index - list.firstVisiblePosition)
        if (t.phase == 3) {
            row?.let { floorAdapter.drawCollector(it, -1, 0f) }
            trip = null
            return
        }
        val progress = if (t.phase == 1) 1f else (now - t.phaseStart).toFloat() / t.walkMs
        row?.let { floorAdapter.drawCollector(it, t.phase, progress) }
    }

    /** Leaving the screen: the trip is dropped (offline earnings collect for the Collector). */
    private fun cancelCollector() {
        val t = trip ?: return
        val list = findViewById<ListView>(R.id.floorList)
        list.getChildAt(t.index - list.firstVisiblePosition)?.let { floorAdapter.drawCollector(it, -1, 0f) }
        trip = null
    }

    /** Empties a room's storage into the bunker's resources, with the "+N" popup and a sound. */
    private fun collectFrom(floor: Floor): Int {
        val s = state ?: return 0
        val amount = floor.takeStock()
        if (amount <= 0) return 0
        if (floor === digFloor) s.scrap += amount else s.food += amount
        floor.pendingPopup = amount
        sfx.play(Sfx.Sound.COLLECT)
        floorAdapter.refresh(floorList)
        refreshUpgrades()
        refreshHud()
        return amount
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
            refreshUpgrades()
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
        refreshUpgrades()
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

    /**
     * Tapping a room: the player lends a hand (1 + tools level of progress, into storage) and
     * collects whatever is in storage. Workers work on their own, so they no longer add to taps.
     */
    private fun onFloorTapped(floor: Floor) {
        val s = state ?: return
        val isDig = floor === digFloor
        val tools = s.level(if (isDig) UP_DIG_TOOLS else UP_FARM_TOOLS)
        sfx.play(if (isDig) Sfx.Sound.DIG else Sfx.Sound.HARVEST, 0.92f + Random.nextFloat() * 0.16f)
        floor.work(1 + tools)
        if (collectFrom(floor) == 0) floorAdapter.refresh(floorList)
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
            STORAGE -> updateCapacity(s)
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

    /** Prices in the upgrade sheet follow the scrap count; only redraw them while it is open. */
    private fun refreshUpgrades() {
        if (currentTab != null) upgradeAdapter.notifyDataSetChanged()
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
        if (old == value) return                     // nothing changed: no relayout, no redraw
        view.text = value.toString()
        if (old != null && value > old && !lowDetail) view.startAnimation(AnimationUtils.loadAnimation(this, R.anim.hud_pop))
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
