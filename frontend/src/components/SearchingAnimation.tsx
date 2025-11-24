import './SearchingAnimation.css'

export default function SearchingAnimation() {
  return (
    <div className="searching-animation-container">
      <div className="searching-text matrix-text">
        <span className="matrix-char">S</span>
        <span className="matrix-char">E</span>
        <span className="matrix-char">A</span>
        <span className="matrix-char">R</span>
        <span className="matrix-char">C</span>
        <span className="matrix-char">H</span>
        <span className="matrix-char">I</span>
        <span className="matrix-char">N</span>
        <span className="matrix-char">G</span>
      </div>
      <div className="matrix-particles">
        {Array.from({ length: 20 }).map((_, i) => (
          <span key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 2}s`,
            animationDuration: `${1 + Math.random() * 2}s`
          }}>
            {String.fromCharCode(0x30A0 + Math.floor(Math.random() * 96))}
          </span>
        ))}
      </div>
    </div>
  )
}

