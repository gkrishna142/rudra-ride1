import React from 'react';
import { useTheme } from '../../context/ThemeContext';
import { 
  FiSun, FiMoon, FiMaximize2, FiMinimize2, 
  FiType, FiDroplet, FiZap, FiRotateCw,
  FiAlignLeft, FiAlignRight, FiSidebar
} from 'react-icons/fi';
import './ThemeSettings.css';

const ThemeSettings = () => {
  const { theme, updateTheme, resetTheme } = useTheme();

  const themeOptions = [
    {
      id: 'mode',
      label: 'Theme Mode',
      icon: theme.mode === 'light' ? FiSun : FiMoon,
      options: [
        { value: 'light', label: 'Light', icon: FiSun },
        { value: 'dark', label: 'Dark', icon: FiMoon },
      ],
    },
    {
      id: 'layout',
      label: 'Layout Style',
      icon: theme.layout === 'full-width' ? FiMaximize2 : FiMinimize2,
      options: [
        { value: 'full-width', label: 'Full Width', icon: FiMaximize2 },
        { value: 'boxed', label: 'Boxed', icon: FiMinimize2 },
      ],
    },
    {
      id: 'sidebarPosition',
      label: 'Sidebar Position',
      icon: theme.sidebarPosition === 'left' ? FiAlignLeft : FiAlignRight,
      options: [
        { value: 'left', label: 'Left', icon: FiAlignLeft },
        { value: 'right', label: 'Right', icon: FiAlignRight },
      ],
    },
    {
      id: 'sidebarBehavior',
      label: 'Sidebar Behavior',
      icon: FiSidebar,
      options: [
        { value: 'fixed', label: 'Fixed', icon: FiSidebar },
        { value: 'collapsible', label: 'Collapsible', icon: FiSidebar },
      ],
    },
    {
      id: 'fontSize',
      label: 'Font Size',
      icon: FiType,
      options: [
        { value: 'small', label: 'Small' },
        { value: 'medium', label: 'Medium' },
        { value: 'large', label: 'Large' },
      ],
    },
    {
      id: 'colorScheme',
      label: 'Color Scheme',
      icon: FiDroplet,
      options: [
        { value: 'default', label: 'Default', color: '#3b82f6' },
        { value: 'blue', label: 'Blue', color: '#3b82f6' },
        { value: 'green', label: 'Green', color: '#10b981' },
        { value: 'purple', label: 'Purple', color: '#8b5cf6' },
        { value: 'orange', label: 'Orange', color: '#f97316' },
      ],
    },
  ];

  const handleToggle = (key, value) => {
    updateTheme({ [key]: value });
  };

  return (
    <div className="theme-settings">
      <div className="theme-settings-header">
        <h2>Theme Customization</h2>
        <button className="btn-reset" onClick={resetTheme}>
          <FiRotateCw /> Reset to Default
        </button>
      </div>

      <div className="theme-settings-grid">
        {themeOptions.map((option) => (
          <div key={option.id} className="theme-option-card">
            <div className="theme-option-header">
              <option.icon className="theme-option-icon" />
              <h3>{option.label}</h3>
            </div>
            <div className="theme-option-buttons">
              {option.options.map((opt) => {
                const isActive = theme[option.id] === opt.value;
                const Icon = opt.icon;
                
                return (
                  <button
                    key={opt.value}
                    className={`theme-option-btn ${isActive ? 'active' : ''}`}
                    onClick={() => handleToggle(option.id, opt.value)}
                    title={opt.label}
                  >
                    {Icon && <Icon />}
                    {opt.color && (
                      <span 
                        className="color-preview" 
                        style={{ backgroundColor: opt.color }}
                      />
                    )}
                    <span>{opt.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        <div className="theme-option-card">
          <div className="theme-option-header">
            <FiZap className="theme-option-icon" />
            <h3>Animations</h3>
          </div>
          <div className="theme-toggle-switch">
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={theme.animations}
                onChange={(e) => updateTheme({ animations: e.target.checked })}
              />
              <span className="slider"></span>
            </label>
            <span className="toggle-label">
              {theme.animations ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>

        <div className="theme-option-card">
          <div className="theme-option-header">
            <FiRotateCw className="theme-option-icon" />
            <h3>Text Direction</h3>
          </div>
          <div className="theme-option-buttons">
            <button
              className={`theme-option-btn ${theme.direction === 'ltr' ? 'active' : ''}`}
              onClick={() => handleToggle('direction', 'ltr')}
            >
              LTR
            </button>
            <button
              className={`theme-option-btn ${theme.direction === 'rtl' ? 'active' : ''}`}
              onClick={() => handleToggle('direction', 'rtl')}
            >
              RTL
            </button>
          </div>
        </div>
      </div>

      <div className="theme-preview">
        <h3>Preview</h3>
        <div className="preview-card">
          <div className="preview-header">
            <div className="preview-avatar"></div>
            <div>
              <div className="preview-title"></div>
              <div className="preview-subtitle"></div>
            </div>
          </div>
          <div className="preview-content">
            <div className="preview-line"></div>
            <div className="preview-line short"></div>
            <div className="preview-line"></div>
          </div>
          <div className="preview-footer">
            <div className="preview-button"></div>
            <div className="preview-button"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThemeSettings;

