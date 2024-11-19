const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    name: { type: String, required: true },
    email: { type: String, required: true },
    age: { type: Number, required: true },
    height: { type: Number, required: true },
    weight: { type: Number, required: true },
    goal: { type: String, required: true },
});

const User = mongoose.model('User', userSchema);

module.exports = User; // Export the model
