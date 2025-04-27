import axios from "axios";
import { ProcessImageResponse, GetScreenshotsResponse } from "../types";

const api = axios.create({
  baseURL: "http://localhost:8000/api", // Django backend URL
});

// Helper function to get full image URL
const getFullImageUrl = (url: string) => {
  if (url.startsWith("http")) return url;
  return `http://localhost:8000${url.startsWith("/") ? url : `/${url}`}`;
};

export const processImage = async (
  file: File
): Promise<ProcessImageResponse> => {
  const formData = new FormData();
  formData.append("image", file);

  try {
    const response = await api.post("/process-image/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    // Ensure all image URLs are absolute
    if (response.data.screenshots) {
      response.data.screenshots = response.data.screenshots.map(
        (screenshot: any) => ({
          ...screenshot,
          url: getFullImageUrl(screenshot.url),
        })
      );
    }

    return response.data;
  } catch (error) {
    console.error("Error processing image:", error);
    throw error;
  }
};

export const getScreenshots = async (
  recordId: number
): Promise<GetScreenshotsResponse> => {
  try {
    const response = await api.get(`/screenshots/${recordId}/`);

    // Ensure all image URLs are absolute
    if (response.data.screenshots) {
      response.data.screenshots = response.data.screenshots.map(
        (screenshot: any) => ({
          ...screenshot,
          url: getFullImageUrl(screenshot.url),
        })
      );
    }

    return response.data;
  } catch (error) {
    console.error("Error fetching screenshots:", error);
    throw error;
  }
};
