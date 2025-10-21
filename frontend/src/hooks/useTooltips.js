import { useState, useEffect } from 'react';
import tooltipsData from '../data/tooltips.json';

/**
 * Custom hook to access tooltip content
 * @returns {Object} Object with methods to retrieve tooltips
 */
export const useTooltips = () => {
  const [tooltips, setTooltips] = useState({});

  useEffect(() => {
    // Tooltips are already in nested object format
    if (tooltipsData && tooltipsData.tooltips) {
      setTooltips(tooltipsData.tooltips);
    }
  }, []);

  /**
   * Get tooltip content by category and ID
   * @param {string} category - Tooltip category (e.g., 'athlete_rankings', 'team_rankings')
   * @param {string} id - Tooltip identifier within category
   * @returns {Object|null} Tooltip object with text, placement, trigger
   */
  const getTooltip = (category, id) => {
    return tooltips[category]?.[id] || null;
  };

  /**
   * Get tooltip text by category and ID
   * @param {string} category - Tooltip category
   * @param {string} id - Tooltip identifier
   * @returns {string} Tooltip text or empty string
   */
  const getTooltipText = (category, id) => {
    return tooltips[category]?.[id]?.text || '';
  };

  /**
   * Get all athlete ranking tooltips
   * @returns {Object} All athlete ranking tooltips
   */
  const getAthleteTooltips = () => {
    return tooltips.athlete_rankings || {};
  };

  /**
   * Get all team ranking tooltips
   * @returns {Object} All team ranking tooltips
   */
  const getTeamTooltips = () => {
    return tooltips.team_rankings || {};
  };

  return {
    tooltips,
    getTooltip,
    getTooltipText,
    getAthleteTooltips,
    getTeamTooltips
  };
};
