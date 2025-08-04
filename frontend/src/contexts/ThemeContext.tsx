import React, { createContext, useContext, useState, useEffect } from 'react';

interface ThemeColors {
  // Backgrounds
  background: string;
  cardBackground: string;
  headerBackground: string;
  panelBackground: string;
  
  // Text
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  
  // Borders
  border: string;
  borderLight: string;
  
  // Interactive
  primary: string;
  primaryHover: string;
  success: string;
  successHover: string;
  error: string;
  warning: string;
  info: string;
  
  // Attendance status colors
  statusPresent: string;
  statusAbsent: string;
  statusTardy: string;
  statusExcused: string;
  statusUnset: string;
  
  // Calendar icon filter
  calendarIconFilter: string;
}

const lightTheme: ThemeColors = {
  // Backgrounds
  background: '#ffffff',
  cardBackground: '#f8f9fa',
  headerBackground: '#ffffff',
  panelBackground: '#ffffff',
  
  // Text
  textPrimary: '#212529',
  textSecondary: '#6c757d',
  textMuted: '#adb5bd',
  
  // Borders
  border: '#dee2e6',
  borderLight: '#e9ecef',
  
  // Interactive
  primary: '#0d6efd',
  primaryHover: '#0b5ed7',
  success: '#198754',
  successHover: '#157347',
  error: '#dc3545',
  warning: '#fd7e14',
  info: '#0dcaf0',
  
  // Attendance status colors
  statusPresent: '#198754',
  statusAbsent: '#dc3545',
  statusTardy: '#fd7e14',
  statusExcused: '#6f42c1',
  statusUnset: '#6c757d',
  
  // Calendar icon filter
  calendarIconFilter: 'invert(1)',
};

const darkTheme: ThemeColors = {
  // Backgrounds
  background: '#0d1117',
  cardBackground: '#161b22',
  headerBackground: '#161b22',
  panelBackground: '#21262d',
  
  // Text
  textPrimary: '#e6edf3',
  textSecondary: '#8b949e',
  textMuted: '#6e7681',
  
  // Borders
  border: '#30363d',
  borderLight: '#21262d',
  
  // Interactive
  primary: '#79c0ff',
  primaryHover: '#a5d6ff',
  success: '#238636',
  successHover: '#2ea043',
  error: '#f85149',
  warning: '#fb8500',
  info: '#79c0ff',
  
  // Attendance status colors
  statusPresent: '#2ea043',
  statusAbsent: '#f85149',
  statusTardy: '#fb8500',
  statusExcused: '#a855f7',
  statusUnset: '#8b949e',
  
  // Calendar icon filter
  calendarIconFilter: 'invert(0)',
};

interface ThemeContextType {
  theme: ThemeColors;
  isDark: boolean;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true; // Default to dark mode
  });

  const theme = isDark ? darkTheme : lightTheme;

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  useEffect(() => {
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // Apply CSS custom properties to root
    const root = document.documentElement;
    Object.entries(theme).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`, value);
    });
  }, [isDark, theme]);

  return (
    <ThemeContext.Provider value={{ theme, isDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}; 