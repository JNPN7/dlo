'use client'

import ReactECharts from 'echarts-for-react';
import type { CSSProperties } from 'react';

export interface EChartsRendererProps {
  /** ECharts option configuration */
  option: Record<string, any>;
  /** Additional CSS class names */
  className?: string;
  /** Custom inline styles (merged with default full-size styles) */
  style?: CSSProperties;
}

/**
 * Core ECharts rendering wrapper with consistent configuration.
 * Encapsulates ReactECharts with standard rendering options.
 */
export function EChartsRenderer({ 
  option, 
  className,
  style 
}: EChartsRendererProps) {
  return (
    <ReactECharts
      option={option}
      className={className}
      style={{ 
        height: '100%', 
        width: '100%',
        ...style 
      }}
      opts={{ renderer: 'canvas' }}
    />
  );
}
