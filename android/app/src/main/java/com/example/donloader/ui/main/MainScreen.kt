package com.example.donloader.ui.main

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.documentfile.provider.DocumentFile
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation3.runtime.NavKey
import com.example.donloader.data.DownloadStatus
import com.example.donloader.data.DownloadTask

// Paleta Catppuccin Mocha
val BaseColor = Color(0xFF1E1E2E)
val SurfaceColor = Color(0xFF313244)
val BorderColor = Color(0xFF45475A)
val TextPrimary = Color(0xFFCDD6F4)
val TextSecondary = Color(0xFFA6ADC8)
val AccentBlue = Color(0xFF89B4FA)
val AccentGreen = Color(0xFFA6E3A1)
val AccentRed = Color(0xFFF38BA8)
val AccentPeach = Color(0xFFF9E2AF)

@Composable
fun MainScreen(
    onItemClick: (NavKey) -> Unit,
    modifier: Modifier = Modifier,
    viewModel: MainScreenViewModel = viewModel(),
) {
    val context = LocalContext.current
    val currentVersionName = remember {
        try {
            context.packageManager.getPackageInfo(context.packageName, 0).versionName ?: "1.2.2"
        } catch (e: Exception) {
            "1.2.2"
        }
    }
    val tasks by viewModel.tasks.collectAsStateWithLifecycle()
    val selectedFolderName by viewModel.selectedFolderName.collectAsStateWithLifecycle()
    val updateInfo by viewModel.updateInfo.collectAsStateWithLifecycle()
    val updateProgress by viewModel.updateProgress.collectAsStateWithLifecycle()

    var urlInput by remember { mutableStateOf("") }
    var selectedFormat by remember { mutableStateOf("MP4") }
    var selectedQuality by remember { mutableStateOf("320k") }

    // Selector SAF para carpetas
    val folderLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocumentTree()
    ) { uri ->
        uri?.let {
            try {
                val takeFlags = Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                context.contentResolver.takePersistableUriPermission(it, takeFlags)

                val documentFile = DocumentFile.fromTreeUri(context, it)
                val displayName = documentFile?.name ?: "Carpeta Seleccionada"
                viewModel.updateSelectedFolder(it.toString(), displayName)
            } catch (e: Exception) {
                // Si falla persistir el permiso
            }
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BaseColor)
            .padding(16.dp)
    ) {
        Column(
            modifier = Modifier.fillMaxSize()
        ) {
            // Cabecera / Título
            Text(
                text = "DonLoader",
                color = TextPrimary,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            // Selector de Carpeta Destino
            Card(
                colors = CardDefaults.cardColors(containerColor = SurfaceColor),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp)
                    .border(1.dp, BorderColor, RoundedCornerShape(12.dp))
            ) {
                Row(
                    modifier = Modifier
                        .clickable { folderLauncher.launch(null) }
                        .padding(14.dp)
                        .fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "📁 Carpeta Destino",
                            color = TextSecondary,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(
                            text = selectedFolderName,
                            color = TextPrimary,
                            fontSize = 13.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                }
            }

            // Input URL
            OutlinedTextField(
                value = urlInput,
                onValueChange = { urlInput = it },
                label = { Text("Pegar URL multimedia aquí", color = TextSecondary) },
                singleLine = true,
                shape = RoundedCornerShape(10.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = AccentBlue,
                    unfocusedBorderColor = BorderColor,
                    focusedTextColor = TextPrimary,
                    unfocusedTextColor = TextPrimary,
                    focusedContainerColor = SurfaceColor,
                    unfocusedContainerColor = SurfaceColor
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp)
            )

            // Selector de Formato (Fila de botones / Chips)
            Text(
                text = "Formato de salida",
                color = TextSecondary,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 6.dp)
            )
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                listOf("MP4", "MKV", "MP3").forEach { format ->
                    val isSelected = selectedFormat == format
                    Button(
                        onClick = { selectedFormat = format },
                        shape = RoundedCornerShape(8.dp),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = if (isSelected) AccentBlue else SurfaceColor,
                            contentColor = if (isSelected) BaseColor else TextPrimary
                        ),
                        modifier = Modifier
                            .weight(1f)
                            .border(1.dp, if (isSelected) Color.Transparent else BorderColor, RoundedCornerShape(8.dp))
                    ) {
                        Text(text = format, fontWeight = FontWeight.Bold)
                    }
                }
            }

            // Selector de Calidad MP3 (Animado / Visible solo para MP3)
            AnimatedVisibility(visible = selectedFormat == "MP3") {
                Column(modifier = Modifier.padding(bottom = 12.dp)) {
                    Text(
                        text = "Calidad de conversión (Audio)",
                        color = TextSecondary,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(bottom = 6.dp)
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf("128k", "192k", "256k", "320k").forEach { quality ->
                            val isSelected = selectedQuality == quality
                            Button(
                                onClick = { selectedQuality = quality },
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = if (isSelected) AccentPeach else SurfaceColor,
                                    contentColor = if (isSelected) BaseColor else TextPrimary
                                ),
                                modifier = Modifier
                                    .weight(1f)
                                    .border(1.dp, if (isSelected) Color.Transparent else BorderColor, RoundedCornerShape(8.dp))
                            ) {
                                Text(
                                    text = quality,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                }
            }

            // Botón Principal Descargar
            Button(
                onClick = {
                    if (urlInput.isNotBlank()) {
                        viewModel.addDownload(urlInput, selectedFormat, selectedQuality)
                        urlInput = "" // Limpiar input de inmediato
                    }
                },
                enabled = urlInput.isNotBlank(),
                shape = RoundedCornerShape(10.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = AccentBlue,
                    disabledContainerColor = SurfaceColor
                ),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp)
                    .padding(bottom = 16.dp)
            ) {
                Text(
                    text = "Descargar",
                    color = if (urlInput.isNotBlank()) BaseColor else TextSecondary,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
            }

            // Sección de Cola (Título)
            if (tasks.isNotEmpty()) {
                Text(
                    text = "Cola de Descargas",
                    color = TextPrimary,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }

            // LazyColumn para las descargas de la cola
            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f, fill = false),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                items(tasks, key = { it.id }) { task ->
                    DownloadTaskCard(task = task, onCancel = { viewModel.cancelDownload(task.id) })
                }
            }

            Spacer(modifier = Modifier.weight(1f))

            // Footer / Pie de página
            HorizontalDivider(color = BorderColor, thickness = 1.dp, modifier = Modifier.padding(vertical = 8.dp))
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 4.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "DonLoader v$currentVersionName",
                    color = TextSecondary,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold
                )

                val updateStatusText = if (updateInfo?.hasUpdate == true) {
                    "Actualización disponible"
                } else {
                    "Sin actualizaciones"
                }
                val updateStatusColor = if (updateInfo?.hasUpdate == true) {
                    AccentPeach
                } else {
                    AccentGreen
                }

                Text(
                    text = updateStatusText,
                    color = updateStatusColor,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }

        // Diálogo modal de actualización
        if (updateInfo != null) {
            val info = updateInfo!!
            val hasApk = !info.downloadUrl.isNullOrBlank()

            AlertDialog(
                onDismissRequest = {
                    if (updateProgress < 0f) viewModel.dismissUpdateDialog()
                },
                containerColor = SurfaceColor,
                titleContentColor = TextPrimary,
                textContentColor = TextSecondary,
                title = { Text("Nueva actualización", fontWeight = FontWeight.Bold) },
                text = {
                    Column {
                        Text("Está disponible la versión ${info.latestVersion} de DonLoader.")
                        Spacer(modifier = Modifier.height(12.dp))
                        if (updateProgress >= 0f) {
                            Text(
                                text = "Descargando: ${updateProgress.toInt()}%",
                                fontWeight = FontWeight.Bold,
                                color = AccentBlue,
                                modifier = Modifier.padding(bottom = 8.dp)
                            )
                            LinearProgressIndicator(
                                progress = { updateProgress / 100f },
                                modifier = Modifier.fillMaxWidth(),
                                color = AccentBlue,
                                trackColor = BorderColor
                            )
                        } else if (updateProgress == -2f) {
                            Text(
                                text = "Error al descargar la actualización. Intentá más tarde.",
                                color = AccentRed,
                                fontWeight = FontWeight.Bold
                            )
                        } else {
                            if (hasApk) {
                                Text("¿Deseas descargar e instalar ahora?")
                            } else {
                                Text("El instalador APK automático no está disponible para esta versión en GitHub. ¿Deseas visitar la página de lanzamientos para descargarla manualmente?")
                            }
                        }
                    }
                },
                confirmButton = {
                    if (updateProgress < 0f) {
                        Button(
                            onClick = {
                                if (hasApk) {
                                    viewModel.startAppUpdate(info.downloadUrl!!)
                                } else {
                                    // Abrir navegador web en GitHub Releases
                                    try {
                                        val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/NicoDolade/DonLoader/releases"))
                                        context.startActivity(intent)
                                    } catch (e: Exception) {
                                        // Error al abrir
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = AccentBlue, contentColor = BaseColor)
                        ) {
                            Text(if (hasApk) "Actualizar" else "Ver en GitHub", fontWeight = FontWeight.Bold)
                        }
                    }
                },
                dismissButton = {
                    if (updateProgress < 0f) {
                        TextButton(onClick = { viewModel.dismissUpdateDialog() }) {
                            Text("Omitir", color = TextSecondary)
                        }
                    }
                }
            )
        }
    }
}

@Composable
fun DownloadTaskCard(
    task: DownloadTask,
    onCancel: () -> Unit
) {
    val statusColor = when (task.status) {
        DownloadStatus.COMPLETADO -> AccentGreen
        DownloadStatus.FALLIDO -> AccentRed
        DownloadStatus.DESCARGANDO -> AccentBlue
        DownloadStatus.EN_COLA -> TextSecondary
        DownloadStatus.EXTRAYENDO -> AccentPeach
        DownloadStatus.CONVIRTIENDO -> AccentPeach
    }

    val statusText = when (task.status) {
        DownloadStatus.EN_COLA -> "En cola..."
        DownloadStatus.EXTRAYENDO -> "Extrayendo info..."
        DownloadStatus.DESCARGANDO -> "Descargando... ${task.progress.toInt()}%"
        DownloadStatus.CONVIRTIENDO -> "Convirtiendo formato..."
        DownloadStatus.COMPLETADO -> "Completado"
        DownloadStatus.FALLIDO -> task.error ?: "Error"
    }

    Card(
        colors = CardDefaults.cardColors(containerColor = SurfaceColor),
        shape = RoundedCornerShape(10.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, BorderColor, RoundedCornerShape(10.dp))
    ) {
        Column(
            modifier = Modifier.padding(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    // Título del Video
                    Text(
                        text = task.displayTitle,
                        color = TextPrimary,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.SemiBold,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    // Formato y Calidad
                    Text(
                        text = "${task.format} ${if (task.quality.isNotBlank() && task.format == "MP3") "(${task.quality})" else ""}".trim(),
                        color = TextSecondary,
                        fontSize = 11.sp
                    )
                }

                // Botón de Cancelación (visible solo si no ha finalizado)
                if (task.status != DownloadStatus.COMPLETADO && task.status != DownloadStatus.FALLIDO) {
                    IconButton(
                        onClick = onCancel,
                        modifier = Modifier.size(24.dp)
                    ) {
                        Icon(
                            imageVector = Icons.Default.Close,
                            contentDescription = "Cancelar descarga",
                            tint = AccentRed,
                            modifier = Modifier.size(20.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Barra de Progreso (visible en descarga/conversión)
            if (task.status == DownloadStatus.DESCARGANDO || task.status == DownloadStatus.CONVIRTIENDO) {
                LinearProgressIndicator(
                    progress = { task.progress / 100f },
                    color = AccentBlue,
                    trackColor = BorderColor,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(6.dp)
                        .padding(vertical = 4.dp)
                )
            } else if (task.status == DownloadStatus.COMPLETADO) {
                LinearProgressIndicator(
                    progress = { 1.0f },
                    color = AccentGreen,
                    trackColor = BorderColor,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(6.dp)
                        .padding(vertical = 4.dp)
                )
            }

            Spacer(modifier = Modifier.height(4.dp))

            // Fila de metadatos (Velocidad, ETA y Estado)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = statusText,
                    color = statusColor,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f)
                )

                if (task.status == DownloadStatus.DESCARGANDO && (task.speed.isNotBlank() || (task.eta.isNotBlank() && task.eta != "--:--"))) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (task.speed.isNotBlank()) {
                            Text(
                                text = task.speed,
                                color = TextSecondary,
                                fontSize = 11.sp
                            )
                        }
                        if (task.eta.isNotBlank() && task.eta != "--:--") {
                            Text(
                                text = "ETA: ${task.eta}",
                                color = TextSecondary,
                                fontSize = 11.sp
                            )
                        }
                    }
                }
            }
        }
    }
}
