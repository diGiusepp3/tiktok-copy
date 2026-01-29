import React, { useState } from 'react';
import { Upload as UploadIcon, X, Image, Video } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;

const Upload = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [caption, setCaption] = useState('');
  const [subscribersOnly, setSubscribersOnly] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    // Check file type
    if (!selectedFile.type.startsWith('image/') && !selectedFile.type.startsWith('video/')) {
      toast.error('Please select an image or video file');
      return;
    }

    // Check file size (max 100MB)
    if (selectedFile.size > 100 * 1024 * 1024) {
      toast.error('File size must be less than 100MB');
      return;
    }

    setFile(selectedFile);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(selectedFile);
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('caption', caption);
      formData.append('subscribers_only', subscribersOnly);

      const token = localStorage.getItem('token');
      const res = await axios.post(`${API}/posts/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });

      toast.success('Post uploaded successfully!');
      
      // Reset form
      setFile(null);
      setPreview(null);
      setCaption('');
      setSubscribersOnly(false);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-white pb-20">
      <div className="max-w-2xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">Upload Content</h1>

        {!preview ? (
          <div className="border-2 border-dashed border-zinc-700 rounded-lg p-12 text-center hover:border-purple-500 transition-colors">
            <input
              type="file"
              accept="image/*,video/*"
              onChange={handleFileChange}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <UploadIcon size={64} className="mx-auto mb-4 text-zinc-500" />
              <p className="text-xl mb-2">Click to upload</p>
              <p className="text-sm text-zinc-500">Images or videos up to 100MB</p>
            </label>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="relative bg-zinc-900 rounded-lg overflow-hidden">
              {file.type.startsWith('image/') ? (
                <img src={preview} alt="Preview" className="w-full max-h-96 object-contain" />
              ) : (
                <video src={preview} controls className="w-full max-h-96" />
              )}
              <button
                onClick={clearFile}
                className="absolute top-4 right-4 bg-black/50 p-2 rounded-full hover:bg-black/70 transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Caption</label>
              <textarea
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                placeholder="Write a caption..."
                className="w-full px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none"
                rows="4"
              />
            </div>

            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="subscribers-only"
                checked={subscribersOnly}
                onChange={(e) => setSubscribersOnly(e.target.checked)}
                className="w-5 h-5 rounded border-zinc-700 bg-zinc-900 text-purple-600 focus:ring-purple-500"
              />
              <label htmlFor="subscribers-only" className="text-sm">
                Subscribers only (exclusive content)
              </label>
            </div>

            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Post'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;
