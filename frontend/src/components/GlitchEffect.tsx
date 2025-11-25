import { useEffect, useState } from 'react'
import './GlitchEffect.css'

interface GlitchEffectProps {
  text: string
  className?: string
}

export default function GlitchEffect({ text, className = '' }: GlitchEffectProps) {
  const [glitch, setGlitch] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      setGlitch(true)
      setTimeout(() => setGlitch(false), 100)
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <span className={`glitch-text ${glitch ? 'glitch-active' : ''} ${className}`} data-text={text}>
      {text}
    </span>
  )
}
