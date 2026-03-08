import { useState } from "react";
import { motion } from "framer-motion";
import confetti from "canvas-confetti";

function glitterBurst() {
  const duration = 600;
  const end = Date.now() + duration;

  const frame = () => {
    confetti({ particleCount: 4, angle: 60, spread: 55, origin: { x: 0 } });
    confetti({ particleCount: 4, angle: 120, spread: 55, origin: { x: 1 } });

    if (Date.now() < end) {
      requestAnimationFrame(frame);
    }
  };

  frame();
}

export default function AnimatedButton({
  children,
  className = "",
  disabled = false,
  type = "button",
  onClick,
  withConfetti = false,
}) {
  const [ripples, setRipples] = useState([]);

  const handleClick = (event) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    const id = Date.now() + Math.random();

    setRipples((prev) => [...prev, { id, x, y, size }]);
    window.setTimeout(() => {
      setRipples((prev) => prev.filter((ripple) => ripple.id !== id));
    }, 550);

    if (onClick) {
      onClick(event);
    }

    if (withConfetti && !disabled) {
      glitterBurst();
    }
  };

  return (
    <motion.button
      type={type}
      disabled={disabled}
      whileHover={!disabled ? { scale: 1.05, boxShadow: "0 12px 26px rgba(79, 70, 229, 0.28)" } : {}}
      whileTap={!disabled ? { scale: 0.96 } : {}}
      onClick={handleClick}
      className={`relative overflow-hidden transition disabled:cursor-not-allowed disabled:opacity-60 ${className}`}
    >
      {children}
      {ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="pointer-events-none absolute rounded-full bg-white/40 animate-ripple"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: ripple.size,
            height: ripple.size,
          }}
        />
      ))}
    </motion.button>
  );
}
