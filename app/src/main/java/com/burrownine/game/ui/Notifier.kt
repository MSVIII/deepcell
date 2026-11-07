package com.burrownine.game.ui

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.burrownine.game.GameActivity
import com.burrownine.game.R

/** Status-bar notifications (Module 8): channel + NotificationCompat.Builder + PendingIntent. */
object Notifier {
    private const val CHANNEL_ID = "bunker_alerts"
    const val ID_BOSS_CLEARED = 1
    const val ID_HATCH_BREACHED = 2

    /** Safe to call many times; Android ignores a channel that already exists. */
    fun createChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                context.getString(R.string.channel_name),
                NotificationManager.IMPORTANCE_DEFAULT
            )
            channel.description = context.getString(R.string.channel_description)
            val manager = context.getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    fun show(context: Context, id: Int, title: String, text: String) {
        // Android 13+ needs the POST_NOTIFICATIONS permission (requested in MainActivity).
        if (Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS)
            != PackageManager.PERMISSION_GRANTED
        ) return

        // Tapping the notification reopens the game screen.
        val intent = Intent(context, GameActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val pending = PendingIntent.getActivity(
            context, id, intent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_hatch)
            .setContentTitle(title)
            .setContentText(text)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pending)
            .setAutoCancel(true)
            .build()
        NotificationManagerCompat.from(context).notify(id, notification)
    }
}
