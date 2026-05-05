import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import axios from 'axios';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  // Definición de tipos para evitar errores de 'unknown'
  image: File | null = null;
  prediction: string = '';
  imageName: string = '';
  probs: Record<string, number> | null = null; // Diccionario de clase: probabilidad

  // URL del backend local para tus pruebas en Lima
  apiUrl: string = 'http://localhost:5000';

  /**
   * Maneja el cambio de archivo con tipado estricto para HTMLInputElement
   */
  handleFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.image = input.files[0];
      this.prediction = '';
      this.imageName = '';
      this.probs = null;
    }
  }

  /**
   * Envía la imagen al servidor Flask y procesa la respuesta
   */
  async handleSubmit(): Promise<void> {
    if (!this.image) return;

    const formData = new FormData();
    formData.append('image', this.image);

    try {
      // Realizamos la petición y aseguramos el tipo de la respuesta
      const res = await axios.post(`${this.apiUrl}/api/clasificar`, formData);
      const data = res.data as { 
        prediction: string; 
        image_name: string; 
        probs: Record<string, number> 
      };

      this.prediction = data.prediction;
      this.imageName = data.image_name;
      this.probs = data.probs;
    } catch (err) {
      alert("Error al conectar con el servidor Flask. Revisa que el backend esté corriendo.");
      console.error(err);
    }
  }

  /**
   * Getters para resolver las rutas de archivos estáticos
   */
  get imageUrl(): string {
    return this.imageName ? `${this.apiUrl}/static/uploads/${this.imageName}` : '';
  }

  get graphUrl(): string {
    // El timestamp (?t=) previene que el navegador use una imagen vieja de la caché
    return this.imageName 
      ? `${this.apiUrl}/static/uploads/probabilidades.png?t=${new Date().getTime()}` 
      : '';
  }

  /**
   * Convierte el objeto de probabilidades en un array tipado para el @for del HTML
   */
  get probEntries(): [string, number][] {
    return this.probs ? (Object.entries(this.probs) as [string, number][]) : [];
  }
}