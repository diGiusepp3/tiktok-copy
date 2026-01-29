import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';

const AuthScreen = () => {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    displayName: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isLogin) {
        const result = await login(formData.username, formData.password);
        if (result.success) {
          toast.success('Welcome back!');
        } else {
          toast.error(result.error);
        }
      } else {
        if (!formData.email || !formData.username || !formData.password) {
          toast.error('Please fill in all fields');
          setLoading(false);
          return;
        }
        const result = await register(
          formData.username,
          formData.email,
          formData.password,
          formData.displayName || formData.username
        );
        if (result.success) {
          toast.success('Account created successfully!');
        } else {
          toast.error(result.error);
        }
      }
    } catch (error) {
      toast.error('Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-black to-pink-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">🔥 AdultTok</h1>
          <p className="text-gray-400">The adult content platform</p>
        </div>

        <div className="bg-zinc-900 rounded-lg p-8 shadow-2xl border border-zinc-800">
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-all ${
                isLogin
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                  : 'bg-zinc-800 text-gray-400 hover:bg-zinc-700'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2 px-4 rounded-lg font-semibold transition-all ${
                !isLogin
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                  : 'bg-zinc-800 text-gray-400 hover:bg-zinc-700'
              }`}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Username
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="Enter your username"
                required
              />
            </div>

            {!isLogin && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                    placeholder="Enter your email"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Display Name
                  </label>
                  <input
                    type="text"
                    name="displayName"
                    value={formData.displayName}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                    placeholder="How should we call you?"
                  />
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="Enter your password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Please wait...' : isLogin ? 'Login' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="text-purple-400 hover:text-purple-300 font-semibold"
              >
                {isLogin ? 'Register' : 'Login'}
              </button>
            </p>
          </div>
        </div>

        <div className="mt-6 text-center text-gray-500 text-sm">
          <p>18+ Only • By continuing, you agree to our Terms</p>
        </div>
      </div>
    </div>
  );
};

export default AuthScreen;
