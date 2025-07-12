"use client"

import { useState, useEffect } from "react"

export default function Header() {
  const [activeSection, setActiveSection] = useState("")
  const [showBackToTop, setShowBackToTop] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      const sections = ["features", "how-it-works"]
      const scrollPosition = window.scrollY + 100

      // Show back to top button when scrolled down
      setShowBackToTop(window.scrollY > 300)

      for (const section of sections) {
        const element = document.getElementById(section)
        if (element) {
          const { offsetTop, offsetHeight } = element
          if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
            setActiveSection(section)
            break
          }
        }
      }
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ 
        behavior: "smooth",
        block: "start"
      })
    }
  }

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    })
  }

  return (
    <>
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="logo" onClick={scrollToTop} style={{ cursor: "pointer" }}>
              <img src="/sumlytic-logo.png" alt="Sumlytic Logo" className="logo-img" height={60} width={180} />
              {/* <div className="logo-text-group">
                <span className="logo-text">Sumlytic</span>
                <span className="logo-slogan">From Real People, To Real Decisions.</span>
              </div> */}
            </div>

            <nav className="nav">
              <a 
                href="#features" 
                className={`nav-link ${activeSection === "features" ? "active" : ""}`}
                onClick={(e) => {
                  e.preventDefault()
                  scrollToSection("features")
                }}
              >
                Features
              </a>
              <a 
                href="#how-it-works" 
                className={`nav-link ${activeSection === "how-it-works" ? "active" : ""}`}
                onClick={(e) => {
                  e.preventDefault()
                  scrollToSection("how-it-works")
                }}
              >
                How it Works
              </a>
              {/* <a href="#extension" className="nav-link">
                Chrome Extension
              </a> */}
            </nav>

            {/* <button className="cta-button">Get Chrome Extension</button> */}
          </div>
        </div>
      </header>

      {/* Back to Top Button */}
      {showBackToTop && (
        <button 
          className="back-to-top"
          onClick={scrollToTop}
          title="Back to Top"
        >
          ↑
        </button>
      )}
    </>
  )
}
