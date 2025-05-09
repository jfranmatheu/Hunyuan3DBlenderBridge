import bpy
import imageio.v3 as iio  # Use modern imageio.v3 API
import numpy as np
import threading
from collections import deque
import time
from typing import Callable, Optional

from .timer_manager import TimerManager

# Removed requests and io as imageio will handle URL fetching and data.


process_queue = deque()
processed_queue = deque()
thread = None
processing_images_ids = {}


def crop_transparent_or_white_edges(img: np.ndarray, margin: int = 5) -> np.ndarray:
    """
    Recorta las filas y columnas que son completamente blancas o transparentes.
    Deja un margen configurable alrededor del contenido útil.
    """
    assert img.shape[2] == 4, "Se espera una imagen RGBA."

    # Separar canales
    r, g, b, a = img[..., 0], img[..., 1], img[..., 2], img[..., 3]

    # Crear una máscara donde los píxeles NO son blancos ni transparentes
    mask = ~((r == 1.0) & (g == 1.0) & (b == 1.0) | (a == 0.0))

    # Combinar por filas y columnas
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)

    # Obtener índices útiles
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]

    # Aplicar margen
    y_min = max(0, y_min - margin)
    y_max = min(img.shape[0] - 1, y_max + margin)
    x_min = max(0, x_min - margin)
    x_max = min(img.shape[1] - 1, x_max + margin)

    # Recorte
    return img[y_min:y_max+1, x_min:x_max+1]


def get_image_from_url(id: str, url: str) -> bpy.types.Image | None:
    """
    Carga una imagen desde una URL en Blender usando imageio.
    Si una imagen con el 'id' dado ya existe, la devuelve.
    De lo contrario, descarga la imagen, la carga en Blender y la devuelve.
    Devuelve None si la descarga o carga falla.
    """
    global processing_images_ids

    image = bpy.data.images.get(id) 
    
    if image is None:
        print(f"Imagen '{id}' no encontrada. Descargando y procesando con imageio desde {url}...")
        new_image_created = False # Flag to track if we need to clean up a new image on failure
        try:
            # Leer la imagen desde la URL usando imageio
            # imageio.v3.imread can take a URI directly
            try:
                img_array_raw = iio.imread(url,pilmode="RGBA") # Request RGBA to simplify channel handling
            except TimeoutError as e:
                print(e)
                print("Trying again...")
                time.sleep(0.15)
                img_array_raw = iio.imread(url,pilmode="RGBA")

            # imageio might return different dtypes, Blender pixels usually expect float32 (0.0 to 1.0)
            if img_array_raw.dtype == np.uint8:
                img_array_float = img_array_raw.astype(np.float32) / 255.0
            elif img_array_raw.dtype == np.uint16:
                img_array_float = img_array_raw.astype(np.float32) / 65535.0
            elif img_array_raw.dtype == np.float32:
                # Assume it's already in 0-1 range if float32, or clamp/normalize if necessary
                img_array_float = np.clip(img_array_raw, 0.0, 1.0) # Ensure it's in 0-1 range
            else:
                print(f"Error: Tipo de dato no soportado por imageio: {img_array_raw.dtype} para la imagen '{id}'. Intentando convertir.")
                # Fallback: try to convert to uint8 first then to float
                img_array_float = iio.imread(url, mode='RGBA', pilmode="RGBA").astype(np.float32) / 255.0

            # Ensure we have 4 channels (RGBA)
            if len(img_array_float.shape) == 3 and img_array_float.shape[2] == 3: # RGB
                print(f"  Imagen '{id}' es RGB, añadiendo canal alfa.")
                alpha_channel = np.ones((height, width, 1), dtype=np.float32)
                img_array_rgba = np.concatenate((img_array_float, alpha_channel), axis=2)
            elif len(img_array_float.shape) == 3 and img_array_float.shape[2] == 4: # RGBA
                img_array_rgba = img_array_float
            elif len(img_array_float.shape) == 2: # Grayscale
                print(f"  Imagen '{id}' es escala de grises, convirtiendo a RGBA.")
                img_array_gray_3channel = np.stack((img_array_float,)*3, axis=-1) # HxW -> HxWx3
                alpha_channel = np.ones((height, width, 1), dtype=np.float32)
                img_array_rgba = np.concatenate((img_array_gray_3channel, alpha_channel), axis=2)
            else:
                print(f"Error: Número de canales no soportado ({img_array_float.shape}) para la imagen '{id}' tras conversión.")
                return None

            img_array_rgba = crop_transparent_or_white_edges(img_array_rgba, margin=5)
            height, width = img_array_rgba.shape[0], img_array_rgba.shape[1]

            image = bpy.data.images.new(name=id, width=width, height=height, alpha=True)
            new_image_created = True

            # Blender expects pixels from bottom-left, some image formats are top-left.
            # imageio.imread with default plugins usually gives top-left (standard for many formats).
            # So, we might need to flip it vertically.
            # However, bpy.types.Image.pixels expects a 1D array (R,G,B,A,R,G,B,A...)
            # and seems to handle the y-inversion internally or expects top-to-bottom rows.
            # Let's try direct assignment first. If inverted, uncomment flipud.
            img_array_rgba_flipped = np.flipud(img_array_rgba)
            image.pixels.foreach_set(img_array_rgba_flipped.ravel())

            # image.pack() # Opcional: empaqueta los datos de la imagen en el archivo .blend

            print(f"Imagen '{id}' cargada y procesada con imageio.")

        except Exception as e:
            print(f"Error al cargar la imagen '{id}' desde {url} con imageio: {e}")
            if new_image_created and image and image.users == 0 : 
                # Si creamos una nueva imagen y no tiene usuarios (no se asignó a nada), la eliminamos.
                bpy.data.images.remove(image)
            if id in processing_images_ids:
                del processing_images_ids[id]
            return None
    else:
        print(f"Imagen '{id}' ya existe en Blender. Usando la existente.")
        if id in processing_images_ids:
            del processing_images_ids[id]

    return image


def wait_for_image_processing():
    global processed_queue
    while len(processed_queue) > 0:
        id, image, on_complete_callback, on_error_callback = processed_queue.popleft()
        if image is not None:
            if on_complete_callback is not None and callable(on_complete_callback):
                on_complete_callback(image)
        else:
            if on_error_callback is not None and callable(on_error_callback):
                on_error_callback()
        global processing_images_ids
        if id in processing_images_ids:
            del processing_images_ids[id]

    global thread
    if thread is None or not thread.is_alive():
        return None
    return 0.5

def process_image_thread():
    global process_queue, processed_queue
    while len(process_queue) > 0:
        id, url, on_complete_callback, on_error_callback = process_queue.popleft()
        image = get_image_from_url(id, url)
        print("Thread: image was processed", image)
        processed_queue.append((id, image, on_complete_callback, on_error_callback))
        time.sleep(0.15)

    global thread
    thread = None
    return None


def request_image_load(id: str, url: str,
                       on_complete_callback: Optional[Callable[[bpy.types.Image], None]] = None,
                       on_error_callback: Optional[Callable[[], None]] = None):
    global process_queue, thread, processing_images_ids
    
    if id in processing_images_ids and processing_images_ids[id]:
        return
    processing_images_ids[id] = True

    # Add the request to the queue
    process_queue.append((id, url, on_complete_callback, on_error_callback))

    # # If no thread is running, start one...
    if thread is None or not thread.is_alive():
        thread = threading.Thread(target=process_image_thread)
        thread.start()

    # If no timer is running, start one...
    if not TimerManager.exists('image_processing'):
        TimerManager.add('image_processing', wait_for_image_processing, first_interval=0.1)



def register():
    from ..utils import TimerManager
    
    def test_image_url():
        # test function...
        request_image_load('blender_logo_test', "https://img.freepik.com/free-photo/kitty-with-monochrome-wall-her_23-2148955134.jpg?t=st=1746573770~exp=1746577370~hmac=a3d49e454130fad30dba761ab636d7268e224de12e4c9e66b634a74f7af274dd&w=740",
                           lambda image: print(f"Imagen '{image}' cargada con éxito."),
                           lambda: print(f"Error al cargar la imagen."))
        return None
    TimerManager.add('test_image_url', test_image_url, first_interval=5)
