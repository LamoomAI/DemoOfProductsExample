import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  console.log('Rendering Footer component');

  return (
    <footer className="bg-gray-800 text-white p-4">
      <div className="container mx-auto text-center">
        <div className="mb-2">
          <Link to="/" className="text-white hover:text-gray-300">Home</Link>
          <span className="mx-2">|</span>
          <Link to="/about" className="text-white hover:text-gray-300">About</Link>
          <span className="mx-2">|</span>
          <Link to="/contact" className="text-white hover:text-gray-300">Contact</Link>
        </div>
        <div>
          <p>&copy; {new Date().getFullYear()} My Application. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;