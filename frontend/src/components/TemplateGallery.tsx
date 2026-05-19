import React from 'react';
import { motion } from 'framer-motion';

export interface StartupTemplate {
  id: string;
  icon: string;
  title: string;
  tagline: string;
  prompt: string;
  color: string;
}

export const TEMPLATES: StartupTemplate[] = [
  {
    id: 'b2b-saas',
    icon: '🏢',
    title: 'B2B SaaS Platform',
    tagline: 'Enterprise subscription software',
    prompt: 'A B2B SaaS platform that uses AI to automate compliance workflows for mid-sized financial institutions, reducing manual audit time by 80%.',
    color: '#3b82f6' // Blue
  },
  {
    id: 'd2c-ecommerce',
    icon: '🛍️',
    title: 'D2C E-commerce',
    tagline: 'Direct-to-consumer brand',
    prompt: 'A premium direct-to-consumer sustainable coffee brand targeting eco-conscious millennials, with a subscription model and zero-waste packaging.',
    color: '#10b981' // Emerald
  },
  {
    id: 'fintech-app',
    icon: '💳',
    title: 'FinTech App',
    tagline: 'Consumer finance & banking',
    prompt: 'A mobile FinTech app designed for freelancers and gig workers that automatically handles tax withholding, expense tracking, and provides micro-advances.',
    color: '#8b5cf6' // Violet
  },
  {
    id: 'health-tech',
    icon: '🏥',
    title: 'HealthTech Solution',
    tagline: 'Digital health & wellness',
    prompt: 'A telehealth platform specifically for chronic care management that integrates with wearable devices to provide doctors with real-time patient vitals.',
    color: '#ec4899' // Pink
  },
  {
    id: 'ai-dev-tool',
    icon: '⚡',
    title: 'AI DevTool',
    tagline: 'Developer productivity',
    prompt: 'An AI-powered IDE extension that automatically writes unit tests and documentation for legacy codebases during the refactoring process.',
    color: '#f59e0b' // Amber
  },
  {
    id: 'marketplace',
    icon: '🤝',
    title: 'Two-Sided Marketplace',
    tagline: 'Connecting supply & demand',
    prompt: 'A hyper-local peer-to-peer marketplace for renting high-end photography and videography equipment safely with built-in insurance.',
    color: '#06b6d4' // Cyan
  }
];

interface TemplateGalleryProps {
  onSelect: (prompt: string) => void;
  disabled?: boolean;
}

export default function TemplateGallery({ onSelect, disabled }: TemplateGalleryProps) {
  return (
    <div style={{ width: '100%', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '1rem'
      }}>
        <h3 style={{ 
          fontSize: '0.9rem', 
          fontWeight: 600, 
          color: '#94a3b8', 
          textTransform: 'uppercase', 
          letterSpacing: '0.05em',
          margin: 0
        }}>
          Or start with a template
        </h3>
      </div>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '1rem',
      }}>
        {TEMPLATES.map((template, i) => (
          <motion.div
            key={template.id}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            onClick={() => !disabled && onSelect(template.prompt)}
            style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '0.75rem',
              padding: '1.25rem',
              cursor: disabled ? 'not-allowed' : 'pointer',
              opacity: disabled ? 0.5 : 1,
              position: 'relative',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem',
              transition: 'all 0.3s ease',
            }}
            whileHover={!disabled ? { 
              y: -4, 
              background: 'rgba(255, 255, 255, 0.06)',
              borderColor: `${template.color}50`,
              boxShadow: `0 10px 30px -10px ${template.color}30`
            } : {}}
            whileTap={!disabled ? { scale: 0.98 } : {}}
          >
            {/* Top gradient glow */}
            <div style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '2px',
              background: `linear-gradient(90deg, transparent, ${template.color}, transparent)`,
              opacity: 0.5
            }} />
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '0.5rem',
                background: `${template.color}15`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.2rem',
                border: `1px solid ${template.color}30`
              }}>
                {template.icon}
              </div>
              <div>
                <h4 style={{ margin: 0, fontSize: '1rem', color: '#f8fafc', fontWeight: 600 }}>{template.title}</h4>
                <div style={{ fontSize: '0.75rem', color: template.color }}>{template.tagline}</div>
              </div>
            </div>
            
            <p style={{ 
              margin: 0, 
              fontSize: '0.85rem', 
              color: '#94a3b8', 
              lineHeight: 1.5,
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}>
              "{template.prompt}"
            </p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
