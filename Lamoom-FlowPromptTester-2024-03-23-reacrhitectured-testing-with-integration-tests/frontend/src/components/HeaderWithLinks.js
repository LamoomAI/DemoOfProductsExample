import React from 'react';
import Logo from './Logo';
import NavigationLink from './NavigationLink';

const HeaderWithLinks = () => {
  console.log('Rendering HeaderWithLinks component');

  return (
    <header className="bg-white shadow-md py-4 px-6 flex items-center justify-between">
      <Logo />
      <nav>
        <ul className="flex">
          <li><NavigationLink href="/" label="Home" /></li>
          <li><NavigationLink href="/about" label="About" /></li>
          <li><NavigationLink href="/services" label="Services" /></li>
          <li><NavigationLink href="/contact" label="Contact" /></li>
        </ul>
      </nav>
    </header>
  );
};

export default HeaderWithLinks;