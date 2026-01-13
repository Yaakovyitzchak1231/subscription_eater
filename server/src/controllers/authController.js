const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

const register = async (req, res) => {
  const { email, password } = req.body;
  console.log(`Attempting registration for: ${email}`);
  
  try {
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await prisma.user.create({
      data: { email, password: hashedPassword }
    });
    const token = jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET);
    console.log('Registration successful');
    res.status(201).json({ token, user: { id: user.id, email: user.email } });
  } catch (error) {
    console.error('Registration Error Detailed:', error);
    res.status(400).json({ error: 'User already exists or invalid data', details: error.message });
  }
};

const login = async (req, res) => {
  const { email, password } = req.body;
  console.log(`Attempting login for: ${email}`);
  
  try {
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      console.log('User not found');
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      console.log('Invalid password');
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET);
    console.log('Login successful');
    res.json({ token, user: { id: user.id, email: user.email } });
  } catch (error) {
    console.error('Login Error Detailed:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
};

module.exports = { register, login };
