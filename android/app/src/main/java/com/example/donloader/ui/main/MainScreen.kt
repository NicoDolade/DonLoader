package com.example.donloader.ui.main

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.documentfile.provider.DocumentFile
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation3.runtime.NavKey
import coil.compose.AsyncImage
import com.example.donloader.R
import com.example.donloader.data.DownloadStatus
import com.example.donloader.data.DownloadTask
import com.example.donloader.data.EngineStatus
import com.example.donloader.data.VideoQualityState
import com.example.donloader.theme.DonLoaderAmber
import com.example.donloader.theme.DonLoaderBackground
import com.example.donloader.theme.DonLoaderBorder
import com.example.donloader.theme.DonLoaderCoral
import com.example.donloader.theme.DonLoaderGreen
import com.example.donloader.theme.DonLoaderRed
import com.example.donloader.theme.DonLoaderSurface
import com.example.donloader.theme.DonLoaderSurfaceElevated
import com.example.donloader.theme.DonLoaderTextPrimary
import com.example.donloader.theme.DonLoaderTextSecondary

@Composable
fun MainScreen(
    onItemClick: (NavKey) -> Unit,
    modifier: Modifier = Modifier,
    viewModel: MainScreenViewModel = viewModel(),
) {
    val context = LocalContext.current
    val clipboardManager = LocalClipboardManager.current
    val currentVersionName = remember {
        try {
            context.packageManager.getPackageInfo(context.packageName, 0).versionName ?: "1.3.1"
        } catch (_: Exception) {
            "1.3.1"
        }
    }
    val tasks by viewModel.tasks.collectAsStateWithLifecycle()
    val selectedFolderName by viewModel.selectedFolderName.collectAsStateWithLifecycle()
    val engineStatus by viewModel.engineStatus.collectAsStateWithLifecycle()
    val rawVideoQualityState by viewModel.videoQualityState.collectAsStateWithLifecycle()
    val updateInfo by viewModel.updateInfo.collectAsStateWithLifecycle()
    val updateProgress by viewModel.updateProgress.collectAsStateWithLifecycle()

    var urlInput by rememberSaveable { mutableStateOf("") }
    var selectedFormat by rememberSaveable { mutableStateOf("MP4") }
    var selectedQuality by rememberSaveable { mutableStateOf("320k") }
    var selectedVideoQuality by rememberSaveable { mutableStateOf<Int?>(null) }
    var analysisRequestedUrl by rememberSaveable { mutableStateOf("") }

    val currentUrl = urlInput.trim()
    val currentVideoQualityState = when (val state = rawVideoQualityState) {
        is VideoQualityState.Loading ->
            if (state.url == currentUrl && analysisRequestedUrl == currentUrl) state else VideoQualityState.Idle
        is VideoQualityState.Ready ->
            if (state.url == currentUrl && analysisRequestedUrl == currentUrl) state else VideoQualityState.Idle
        is VideoQualityState.Error ->
            if (state.url == currentUrl && analysisRequestedUrl == currentUrl) state else VideoQualityState.Idle
        VideoQualityState.Idle -> VideoQualityState.Idle
    }
    val videoIsReady = currentVideoQualityState is VideoQualityState.Ready
    val engineReady = engineStatus is EngineStatus.UpToDate

    LaunchedEffect(currentVideoQualityState) {
        val state = currentVideoQualityState
        if (state is VideoQualityState.Ready) {
            selectedVideoQuality = state.heights.firstOrNull()
        }
    }

    val folderLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocumentTree()
    ) { uri ->
        uri?.let {
            try {
                val takeFlags = Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                context.contentResolver.takePersistableUriPermission(it, takeFlags)
                val documentFile = DocumentFile.fromTreeUri(context, it)
                viewModel.updateSelectedFolder(it.toString(), documentFile?.name ?: "Carpeta seleccionada")
            } catch (_: Exception) {
                // La carpeta es opcional si el proveedor no permite persistir el permiso.
            }
        }
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(DonLoaderBackground),
        contentAlignment = Alignment.TopCenter,
    ) {
        LazyColumn(
            modifier = Modifier
                .fillMaxWidth()
                .widthIn(max = 720.dp),
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            item { Header(engineStatus = engineStatus) }

            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = DonLoaderSurface),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .border(1.dp, DonLoaderBorder, RoundedCornerShape(12.dp)),
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "Nueva descarga",
                            color = DonLoaderTextPrimary,
                            fontSize = 20.sp,
                            fontWeight = FontWeight.Bold,
                        )
                        Text(
                            text = "Pegá un enlace, analizá el video y elegí una calidad real.",
                            color = DonLoaderTextSecondary,
                            fontSize = 12.sp,
                            modifier = Modifier.padding(top = 4.dp, bottom = 14.dp),
                        )
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            OutlinedTextField(
                                value = urlInput,
                                onValueChange = {
                                    urlInput = it
                                    analysisRequestedUrl = ""
                                    selectedVideoQuality = null
                                },
                                label = { Text("URL del video o audio") },
                                singleLine = true,
                                colors = urlFieldColors(),
                                modifier = Modifier.weight(1f),
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            TextButton(
                                onClick = {
                                    val pasted = clipboardManager.getText()?.text.orEmpty()
                                    if (pasted.isNotBlank()) {
                                        urlInput = pasted.trim()
                                        analysisRequestedUrl = ""
                                        selectedVideoQuality = null
                                    }
                                },
                                contentPadding = PaddingValues(horizontal = 8.dp),
                            ) {
                                Text("Pegar", color = DonLoaderTextPrimary, fontWeight = FontWeight.Bold)
                            }
                        }
                        Text(
                            text = "Formato",
                            color = DonLoaderTextSecondary,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(top = 16.dp, bottom = 6.dp),
                        )
                        FormatSelector(
                            selectedFormat = selectedFormat,
                            onFormatSelected = {
                                selectedFormat = it
                                analysisRequestedUrl = ""
                                selectedVideoQuality = null
                            },
                        )
                        if (selectedFormat == "MP3") {
                            QualitySelector(
                                selectedQuality = selectedQuality,
                                onQualitySelected = { selectedQuality = it },
                            )
                        } else {
                            VideoQualityPicker(
                                state = currentVideoQualityState,
                                selectedQuality = selectedVideoQuality,
                                onQualitySelected = { selectedVideoQuality = it },
                                onAnalyze = {
                                    analysisRequestedUrl = currentUrl
                                    selectedVideoQuality = null
                                    viewModel.analyzeVideoQualities(currentUrl)
                                },
                                analyzeEnabled = currentUrl.isNotBlank() && engineReady,
                            )
                        }
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 14.dp)
                                .clip(RoundedCornerShape(8.dp))
                                .clickable { folderLauncher.launch(null) }
                                .background(DonLoaderSurfaceElevated)
                                .padding(horizontal = 12.dp, vertical = 10.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "Carpeta de destino",
                                    color = DonLoaderTextSecondary,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                )
                                Text(
                                    text = selectedFolderName,
                                    color = DonLoaderTextPrimary,
                                    fontSize = 13.sp,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                )
                            }
                            Text(
                                text = "Cambiar",
                                color = DonLoaderCoral,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                            )
                        }
                        val canDownload = currentUrl.isNotBlank() &&
                            engineReady &&
                            (selectedFormat == "MP3" || videoIsReady)
                        Button(
                            onClick = {
                                viewModel.addDownload(
                                    currentUrl,
                                    selectedFormat,
                                    selectedQuality,
                                    if (selectedFormat == "MP3") null else selectedVideoQuality,
                                )
                                urlInput = ""
                                analysisRequestedUrl = ""
                                selectedVideoQuality = null
                            },
                            enabled = canDownload,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = DonLoaderCoral,
                                contentColor = DonLoaderBackground,
                                disabledContainerColor = DonLoaderSurfaceElevated,
                                disabledContentColor = DonLoaderTextSecondary,
                            ),
                            shape = RoundedCornerShape(8.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 14.dp)
                                .height(48.dp),
                        ) {
                            Text(
                                text = when {
                                    engineStatus is EngineStatus.Updating -> "Esperando motor yt-dlp..."
                                    selectedFormat != "MP3" &&
                                        currentVideoQualityState is VideoQualityState.Loading -> "Analizando video..."
                                    else -> "Añadir a la cola"
                                },
                                fontWeight = FontWeight.Bold,
                            )
                        }
                    }
                }
            }

            item {
                EngineStatusBanner(status = engineStatus, onRetry = { viewModel.refreshEngine() })
            }
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        text = "Cola de descargas · " + tasks.size,
                        color = DonLoaderTextPrimary,
                        fontSize = 17.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.weight(1f),
                    )
                    if (tasks.any { it.status == DownloadStatus.COMPLETADO }) {
                        TextButton(onClick = { viewModel.clearCompleted() }) {
                            Text("Limpiar completadas", color = DonLoaderTextSecondary, fontSize = 12.sp)
                        }
                    }
                }
            }
            if (tasks.isEmpty()) {
                item { EmptyQueue() }
            } else {
                items(tasks, key = { it.id }) { task ->
                    DownloadTaskCard(
                        task = task,
                        onCancel = { viewModel.cancelDownload(task.id) },
                        onRetry = { viewModel.retryDownload(task.id) },
                    )
                }
            }
            item {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                ) {
                    Text(
                        text = "DonLoader v" + currentVersionName,
                        color = DonLoaderTextSecondary,
                        fontSize = 11.sp,
                    )
                    Text(
                        text = if (updateInfo?.hasUpdate == true) "Actualización disponible" else "Sin actualizaciones",
                        color = if (updateInfo?.hasUpdate == true) DonLoaderAmber else DonLoaderGreen,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                    )
                }
            }
        }
        if (updateInfo != null) {
            UpdateDialog(
                info = updateInfo!!,
                progress = updateProgress,
                context = context,
                onDismiss = { viewModel.dismissUpdateDialog() },
                onStartUpdate = { viewModel.startAppUpdate(it) },
            )
        }
    }
}

@Composable
private fun Header(engineStatus: EngineStatus) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "DonLoader",
                color = DonLoaderTextPrimary,
                fontSize = 25.sp,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = "Descargas simples, rápidas y bajo control",
                color = DonLoaderTextSecondary,
                fontSize = 11.sp,
            )
        }
        EngineStatusPill(engineStatus = engineStatus)
    }
}

@Composable
private fun EngineStatusPill(engineStatus: EngineStatus) {
    val label: String
    val color: Color
    when (engineStatus) {
        EngineStatus.Unknown -> {
            label = "Preparando"
            color = DonLoaderAmber
        }
        EngineStatus.UpToDate -> {
            label = "Motor listo"
            color = DonLoaderGreen
        }
        is EngineStatus.Updating -> {
            label = "Actualizando"
            color = DonLoaderAmber
        }
        is EngineStatus.Failed -> {
            label = "Revisar motor"
            color = DonLoaderRed
        }
    }
    Surface(
        color = DonLoaderSurface,
        shape = RoundedCornerShape(20.dp),
        border = BorderStroke(1.dp, DonLoaderBorder),
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 7.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("●", color = color, fontSize = 9.sp)
            Spacer(modifier = Modifier.width(5.dp))
            Text(label, color = DonLoaderTextSecondary, fontSize = 10.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun FormatSelector(selectedFormat: String, onFormatSelected: (String) -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(DonLoaderSurfaceElevated)
            .border(1.dp, DonLoaderBorder, RoundedCornerShape(8.dp))
            .padding(3.dp),
        horizontalArrangement = Arrangement.spacedBy(3.dp),
    ) {
        listOf("MP3", "MP4", "MKV").forEach { format ->
            Box(
                modifier = Modifier
                    .weight(1f)
                    .clip(RoundedCornerShape(6.dp))
                    .background(if (selectedFormat == format) DonLoaderCoral else Color.Transparent)
                    .clickable { onFormatSelected(format) }
                    .padding(vertical = 10.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = format,
                    color = if (selectedFormat == format) DonLoaderBackground else DonLoaderTextPrimary,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                )
            }
        }
    }
}

@Composable
private fun QualitySelector(selectedQuality: String, onQualitySelected: (String) -> Unit) {
    Column(modifier = Modifier.padding(top = 14.dp)) {
        Text(
            text = "Calidad de audio",
            color = DonLoaderTextSecondary,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 6.dp),
        )
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.fillMaxWidth()) {
            listOf("128k", "192k", "256k", "320k").forEach { quality ->
                val selected = quality == selectedQuality
                Box(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(6.dp))
                        .background(if (selected) DonLoaderSurfaceElevated else Color.Transparent)
                        .border(1.dp, if (selected) DonLoaderCoral else DonLoaderBorder, RoundedCornerShape(6.dp))
                        .clickable { onQualitySelected(quality) }
                        .padding(vertical = 9.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = quality,
                        color = if (selected) DonLoaderCoral else DonLoaderTextSecondary,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                    )
                }
            }
        }
    }
}

@Composable
fun VideoQualityPicker(
    state: VideoQualityState,
    selectedQuality: Int?,
    onQualitySelected: (Int?) -> Unit,
    onAnalyze: () -> Unit,
    analyzeEnabled: Boolean,
) {
    var menuExpanded by remember { mutableStateOf(false) }
    val displayedQuality = selectedQuality?.let { it.toString() + "p" } ?: "Mejor disponible"
    Column(modifier = Modifier.padding(top = 14.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "Calidad de video",
                color = DonLoaderTextSecondary,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f),
            )
            OutlinedButton(
                onClick = onAnalyze,
                enabled = analyzeEnabled && state !is VideoQualityState.Loading,
                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp),
                shape = RoundedCornerShape(7.dp),
            ) {
                Text(
                    text = if (state is VideoQualityState.Loading) "Analizando..." else "Analizar",
                    fontSize = 11.sp,
                )
            }
        }
        when (state) {
            VideoQualityState.Idle -> Text(
                text = "Analizá el enlace para ver las resoluciones disponibles.",
                color = DonLoaderTextSecondary,
                fontSize = 11.sp,
                modifier = Modifier.padding(top = 6.dp),
            )
            is VideoQualityState.Loading -> Row(
                modifier = Modifier.padding(top = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                CircularProgressIndicator(
                    modifier = Modifier.size(15.dp),
                    color = DonLoaderAmber,
                    strokeWidth = 2.dp,
                )
                Spacer(modifier = Modifier.width(7.dp))
                Text("Consultando metadata sin descargar...", color = DonLoaderAmber, fontSize = 11.sp)
            }
            is VideoQualityState.Error -> Text(
                text = state.message.ifBlank { "No se pudo analizar el enlace." },
                color = DonLoaderRed,
                fontSize = 11.sp,
                modifier = Modifier.padding(top = 6.dp),
            )
            is VideoQualityState.Ready -> {
                Box(modifier = Modifier.padding(top = 8.dp)) {
                    OutlinedButton(
                        onClick = { if (state.heights.isNotEmpty()) menuExpanded = true },
                        enabled = state.heights.isNotEmpty(),
                        shape = RoundedCornerShape(7.dp),
                        modifier = Modifier.fillMaxWidth(),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 8.dp),
                    ) {
                        Text(
                            text = displayedQuality,
                            color = if (state.heights.isEmpty()) DonLoaderAmber else DonLoaderTextPrimary,
                            modifier = Modifier.fillMaxWidth(),
                        )
                    }
                    DropdownMenu(
                        expanded = menuExpanded,
                        onDismissRequest = { menuExpanded = false },
                    ) {
                        state.heights.forEach { height ->
                            DropdownMenuItem(
                                text = { Text(height.toString() + "p") },
                                onClick = {
                                    onQualitySelected(height)
                                    menuExpanded = false
                                },
                            )
                        }
                    }
                }
                Text(
                    text = if (state.heights.isEmpty()) {
                        "El sitio no informó alturas; se usará la mejor disponible."
                    } else {
                        state.heights.size.toString() +
                            " calidades disponibles · la mayor se selecciona por defecto"
                    },
                    color = if (state.heights.isEmpty()) DonLoaderAmber else DonLoaderGreen,
                    fontSize = 11.sp,
                    modifier = Modifier.padding(top = 5.dp),
                )
            }
        }
    }
}

@Composable
private fun urlFieldColors() = OutlinedTextFieldDefaults.colors(
    focusedBorderColor = DonLoaderCoral,
    unfocusedBorderColor = DonLoaderBorder,
    focusedLabelColor = DonLoaderCoral,
    unfocusedLabelColor = DonLoaderTextSecondary,
    focusedTextColor = DonLoaderTextPrimary,
    unfocusedTextColor = DonLoaderTextPrimary,
    cursorColor = DonLoaderCoral,
    focusedContainerColor = DonLoaderSurfaceElevated,
    unfocusedContainerColor = DonLoaderSurfaceElevated,
)

@Composable
private fun EmptyQueue() {
    Card(
        colors = CardDefaults.cardColors(containerColor = DonLoaderSurface),
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, DonLoaderBorder, RoundedCornerShape(12.dp)),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 30.dp, horizontal = 20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text("↓", color = DonLoaderCoral, fontSize = 28.sp, fontWeight = FontWeight.Bold)
            Text("La cola está vacía", color = DonLoaderTextPrimary, fontWeight = FontWeight.Bold)
            Text(
                "Pegá un enlace para preparar tu primera descarga.",
                color = DonLoaderTextSecondary,
                fontSize = 12.sp,
                modifier = Modifier.padding(top = 4.dp),
            )
        }
    }
}

@Composable
fun DownloadTaskCard(
    task: DownloadTask,
    onCancel: () -> Unit,
    onRetry: () -> Unit = {},
) {
    val statusColor = when (task.status) {
        DownloadStatus.COMPLETADO -> DonLoaderGreen
        DownloadStatus.FALLIDO -> DonLoaderRed
        DownloadStatus.DESCARGANDO -> DonLoaderCoral
        DownloadStatus.EN_COLA -> DonLoaderTextSecondary
        DownloadStatus.EXTRAYENDO, DownloadStatus.CONVIRTIENDO -> DonLoaderAmber
    }
    val statusText = when (task.status) {
        DownloadStatus.EN_COLA -> "En cola..."
        DownloadStatus.EXTRAYENDO -> "Extrayendo info..."
        DownloadStatus.DESCARGANDO -> "Descargando... " + task.progress.toInt() + "%"
        DownloadStatus.CONVIRTIENDO -> "Convirtiendo formato..."
        DownloadStatus.COMPLETADO -> "Completado"
        DownloadStatus.FALLIDO -> task.error ?: "Error"
    }
    val mediaQuality = if (task.format == "MP3") {
        task.format + " · " + task.quality.ifBlank { "320k" }
    } else {
        task.format + " · " + (task.videoQuality?.let { it.toString() + "p" } ?: "Mejor disponible")
    }

    Card(
        colors = CardDefaults.cardColors(containerColor = DonLoaderSurface),
        shape = RoundedCornerShape(10.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, DonLoaderBorder, RoundedCornerShape(10.dp)),
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.Top,
            ) {
                AsyncImage(
                    model = task.thumbnailUrl,
                    contentDescription = "Miniatura del video",
                    placeholder = painterResource(R.drawable.thumb_placeholder),
                    error = painterResource(R.drawable.thumb_placeholder),
                    fallback = painterResource(R.drawable.thumb_placeholder),
                    contentScale = ContentScale.Crop,
                    modifier = Modifier
                        .size(width = 72.dp, height = 48.dp)
                        .clip(RoundedCornerShape(6.dp))
                        .background(DonLoaderSurfaceElevated)
                        .border(1.dp, DonLoaderBorder, RoundedCornerShape(6.dp)),
                )
                Spacer(modifier = Modifier.width(10.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = task.displayTitle,
                        color = DonLoaderTextPrimary,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.SemiBold,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis,
                    )
                    Text(
                        text = mediaQuality,
                        color = DonLoaderTextSecondary,
                        fontSize = 11.sp,
                        modifier = Modifier.padding(top = 4.dp),
                    )
                }
                when (task.status) {
                    DownloadStatus.FALLIDO -> IconButton(
                        onClick = onRetry,
                        modifier = Modifier.size(28.dp),
                    ) {
                        Icon(
                            imageVector = Icons.Default.Refresh,
                            contentDescription = "Reintentar descarga",
                            tint = DonLoaderTextPrimary,
                        )
                    }
                    else -> if (task.status != DownloadStatus.COMPLETADO) {
                        IconButton(
                            onClick = onCancel,
                            modifier = Modifier.size(28.dp),
                        ) {
                            Icon(
                                imageVector = Icons.Default.Close,
                                contentDescription = "Cancelar descarga",
                                tint = DonLoaderRed,
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(9.dp))
            if (task.status == DownloadStatus.DESCARGANDO || task.status == DownloadStatus.CONVIRTIENDO) {
                LinearProgressIndicator(
                    progress = { task.progress / 100f },
                    color = DonLoaderCoral,
                    trackColor = DonLoaderSurfaceElevated,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(5.dp),
                )
            } else if (task.status == DownloadStatus.COMPLETADO) {
                LinearProgressIndicator(
                    progress = { 1f },
                    color = DonLoaderGreen,
                    trackColor = DonLoaderSurfaceElevated,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(5.dp),
                )
            }

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 7.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text(
                    text = statusText,
                    color = statusColor,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    modifier = Modifier.weight(1f),
                )
                if (task.status == DownloadStatus.DESCARGANDO) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        if (task.speed.isNotBlank()) {
                            Text(task.speed, color = DonLoaderTextSecondary, fontSize = 10.sp)
                        }
                        if (task.eta.isNotBlank() && task.eta != "--:--") {
                            Text("ETA " + task.eta, color = DonLoaderTextSecondary, fontSize = 10.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun EngineStatusBanner(status: EngineStatus, onRetry: () -> Unit) {
    when (status) {
        EngineStatus.UpToDate, EngineStatus.Unknown -> Unit
        is EngineStatus.Updating -> StatusBanner(
            color = DonLoaderAmber,
            title = "Actualizando motor yt-dlp",
            detail = "Las descargas se habilitarán al terminar.",
        )
        is EngineStatus.Failed -> StatusBanner(
            color = DonLoaderRed,
            title = "No se pudo actualizar yt-dlp",
            detail = status.message,
            action = {
                TextButton(onClick = onRetry) {
                    Text("Reintentar", color = DonLoaderCoral)
                }
            },
        )
    }
}

@Composable
private fun StatusBanner(
    color: Color,
    title: String,
    detail: String,
    action: (@Composable () -> Unit)? = null,
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = DonLoaderSurface),
        shape = RoundedCornerShape(10.dp),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, color, RoundedCornerShape(10.dp)),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 12.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            if (color == DonLoaderAmber) {
                CircularProgressIndicator(
                    modifier = Modifier.size(17.dp),
                    color = color,
                    strokeWidth = 2.dp,
                )
                Spacer(modifier = Modifier.width(9.dp))
            }
            Column(modifier = Modifier.weight(1f)) {
                Text(title, color = color, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                Text(
                    detail,
                    color = DonLoaderTextSecondary,
                    fontSize = 11.sp,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                )
            }
            action?.invoke()
        }
    }
}

@Composable
private fun UpdateDialog(
    info: com.example.donloader.updater.AppUpdater.UpdateInfo,
    progress: Float,
    context: android.content.Context,
    onDismiss: () -> Unit,
    onStartUpdate: (String) -> Unit,
) {
    val hasApk = !info.downloadUrl.isNullOrBlank()
    AlertDialog(
        onDismissRequest = { if (progress < 0f) onDismiss() },
        containerColor = DonLoaderSurface,
        titleContentColor = DonLoaderTextPrimary,
        textContentColor = DonLoaderTextSecondary,
        title = { Text("Nueva actualización", fontWeight = FontWeight.Bold) },
        text = {
            Column {
                Text("Está disponible la versión " + info.latestVersion + " de DonLoader.")
                Spacer(modifier = Modifier.height(12.dp))
                when {
                    progress >= 0f -> {
                        Text(
                            "Descargando: " + progress.toInt() + "%",
                            color = com.example.donloader.theme.DonLoaderInfo,
                            fontWeight = FontWeight.Bold,
                        )
                        LinearProgressIndicator(
                            progress = { progress / 100f },
                            color = com.example.donloader.theme.DonLoaderInfo,
                            trackColor = DonLoaderBorder,
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 8.dp),
                        )
                    }
                    progress == -2f -> Text(
                        "Error al descargar la actualización. Intentá más tarde.",
                        color = DonLoaderRed,
                    )
                    hasApk -> Text("¿Deseás descargar e instalar ahora?")
                    else -> Text("El APK automático no está disponible. Podés abrir la página de lanzamientos.")
                }
            }
        },
        confirmButton = {
            if (progress < 0f) {
                Button(
                    onClick = {
                        if (hasApk) {
                            onStartUpdate(info.downloadUrl.orEmpty())
                        } else {
                            try {
                                context.startActivity(
                                    Intent(
                                        Intent.ACTION_VIEW,
                                        Uri.parse("https://github.com/NicoDolade/DonLoader/releases"),
                                    ),
                                )
                            } catch (_: Exception) {
                                // El enlace no es esencial para continuar usando la app.
                            }
                        }
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = DonLoaderCoral,
                        contentColor = DonLoaderBackground,
                    ),
                ) {
                    Text(
                        if (hasApk) "Actualizar" else "Ver en GitHub",
                        fontWeight = FontWeight.Bold,
                    )
                }
            }
        },
        dismissButton = {
            if (progress < 0f) {
                TextButton(onClick = onDismiss) {
                    Text("Omitir", color = DonLoaderTextSecondary)
                }
            }
        },
    )
}
