const express = require('express');
const router = express.Router();
const User = require('../models/User'); // Import your Mongoose User model

// Route to add a user
router.post('/add', async (req, res) => {
    try {
        const { name, email, age, height, weight, goal } = req.body;
        const newUser = new User({ name, email, age, height, weight, goal });
        await newUser.save();
        res.status(201).json({ message: 'User added successfully', user: newUser });
    } catch (error) {
        res.status(500).json({ message: 'Error adding user', error });
    }
});

// Route to fetch all users
router.get('/', async (req, res) => {
    try {
        const users = await User.find();
        res.json(users);
    } catch (error) {
        res.status(500).json({ message: 'Error fetching users', error });
    }
});

module.exports = router; // Export the router instance
