import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

const defaultTheme = {
  mode: 'light', // 'light' | 'dark'
  layout: 'full-width', // 'full-width' | 'boxed'
  sidebarPosition: 'left', // 'left' | 'right'
  sidebarBehavior: 'fixed', // 'fixed' | 'collapsible'
  fontSize: 'medium', // 'small' | 'medium' | 'large'
  colorScheme: 'default', // 'default' | 'blue' | 'green' | 'purple' | 'orange'
  animations: true, // true | false
  direction: 'ltr', // 'ltr' | 'rtl'
};

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Load theme from localStorage if available
    const savedTheme = localStorage.getItem('admin-theme');
    if (savedTheme) {
      try {
        return { ...defaultTheme, ...JSON.parse(savedTheme) };
      } catch (e) {
        return defaultTheme;
      }
    }
    return defaultTheme;
  });

  useEffect(() => {
    // Save theme to localStorage whenever it changes
    localStorage.setItem('admin-theme', JSON.stringify(theme));
    
    // Apply theme classes to document root
    const root = document.documentElement;
    
    // Remove old theme classes
    root.classList.remove('theme-light', 'theme-dark');
    root.classList.remove('layout-full-width', 'layout-boxed');
    root.classList.remove('sidebar-left', 'sidebar-right');
    root.classList.remove('font-small', 'font-medium', 'font-large');
    root.classList.remove('color-default', 'color-blue', 'color-green', 'color-purple', 'color-orange');
    root.classList.remove('animations-enabled', 'animations-disabled');
    root.classList.remove('direction-ltr', 'direction-rtl');
    
    // Add new theme classes
    root.classList.add(`theme-${theme.mode}`);
    root.classList.add(`layout-${theme.layout}`);
    root.classList.add(`sidebar-${theme.sidebarPosition}`);
    root.classList.add(`font-${theme.fontSize}`);
    root.classList.add(`color-${theme.colorScheme}`);
    root.classList.add(theme.animations ? 'animations-enabled' : 'animations-disabled');
    root.classList.add(`direction-${theme.direction}`);
    
    // Set direction attribute for RTL support
    root.setAttribute('dir', theme.direction);
  }, [theme]);

  const updateTheme = (updates) => {
    setTheme((prevTheme) => ({ ...prevTheme, ...updates }));
  };

  const resetTheme = () => {
    setTheme(defaultTheme);
  };

  const value = {
    theme,
    updateTheme,
    resetTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};






