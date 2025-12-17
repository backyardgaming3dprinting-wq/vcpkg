#include "command_stack.h"
#include <cassert>
#include <iostream>

using namespace mesh_core;

/**
 * Test command that modifies an integer value
 */
class TestCommand : public Command {
public:
    TestCommand(int& value, int delta, const char* name)
        : value_(value), delta_(delta), name_(name) {}
    
    void execute() override {
        value_ += delta_;
    }
    
    void undo() override {
        value_ -= delta_;
    }
    
    const char* getName() const override {
        return name_;
    }

private:
    int& value_;
    int delta_;
    const char* name_;
};

void test_basic_undo_redo() {
    std::cout << "Running test_basic_undo_redo..." << std::endl;
    
    CommandStack stack;
    int value = 0;
    
    // Initially no undo/redo available
    assert(!stack.canUndo());
    assert(!stack.canRedo());
    assert(stack.undoCount() == 0);
    assert(stack.redoCount() == 0);
    
    // Execute command
    stack.execute(std::make_unique<TestCommand>(value, 5, "Add 5"));
    assert(value == 5);
    assert(stack.canUndo());
    assert(!stack.canRedo());
    assert(stack.undoCount() == 1);
    assert(stack.redoCount() == 0);
    
    // Undo
    assert(stack.undo());
    assert(value == 0);
    assert(!stack.canUndo());
    assert(stack.canRedo());
    assert(stack.undoCount() == 0);
    assert(stack.redoCount() == 1);
    
    // Redo
    assert(stack.redo());
    assert(value == 5);
    assert(stack.canUndo());
    assert(!stack.canRedo());
    assert(stack.undoCount() == 1);
    assert(stack.redoCount() == 0);
    
    std::cout << "✓ test_basic_undo_redo passed" << std::endl;
}

void test_multiple_undo_redo() {
    std::cout << "Running test_multiple_undo_redo..." << std::endl;
    
    CommandStack stack;
    int value = 0;
    
    // Execute multiple commands
    stack.execute(std::make_unique<TestCommand>(value, 10, "Add 10"));
    stack.execute(std::make_unique<TestCommand>(value, 20, "Add 20"));
    stack.execute(std::make_unique<TestCommand>(value, 30, "Add 30"));
    
    assert(value == 60);
    assert(stack.undoCount() == 3);
    assert(stack.redoCount() == 0);
    
    // Undo all
    assert(stack.undo());
    assert(value == 30);
    assert(stack.undo());
    assert(value == 10);
    assert(stack.undo());
    assert(value == 0);
    assert(!stack.canUndo());
    assert(stack.undoCount() == 0);
    assert(stack.redoCount() == 3);
    
    // Redo all
    assert(stack.redo());
    assert(value == 10);
    assert(stack.redo());
    assert(value == 30);
    assert(stack.redo());
    assert(value == 60);
    assert(!stack.canRedo());
    assert(stack.undoCount() == 3);
    assert(stack.redoCount() == 0);
    
    std::cout << "✓ test_multiple_undo_redo passed" << std::endl;
}

void test_redo_cleared_on_new_command() {
    std::cout << "Running test_redo_cleared_on_new_command..." << std::endl;
    
    CommandStack stack;
    int value = 0;
    
    // Execute commands
    stack.execute(std::make_unique<TestCommand>(value, 10, "Add 10"));
    stack.execute(std::make_unique<TestCommand>(value, 20, "Add 20"));
    assert(value == 30);
    
    // Undo one command
    assert(stack.undo());
    assert(value == 10);
    assert(stack.canRedo());
    assert(stack.redoCount() == 1);
    
    // Execute new command - should clear redo stack
    stack.execute(std::make_unique<TestCommand>(value, 5, "Add 5"));
    assert(value == 15);
    assert(!stack.canRedo());
    assert(stack.redoCount() == 0);
    assert(stack.undoCount() == 2);
    
    // Can still undo the commands on undo stack
    assert(stack.undo());
    assert(value == 10);
    assert(stack.undo());
    assert(value == 0);
    
    std::cout << "✓ test_redo_cleared_on_new_command passed" << std::endl;
}

void test_clear_stack() {
    std::cout << "Running test_clear_stack..." << std::endl;
    
    CommandStack stack;
    int value = 0;
    
    // Execute commands
    stack.execute(std::make_unique<TestCommand>(value, 10, "Add 10"));
    stack.execute(std::make_unique<TestCommand>(value, 20, "Add 20"));
    assert(stack.undoCount() == 2);
    
    // Undo one
    assert(stack.undo());
    assert(stack.undoCount() == 1);
    assert(stack.redoCount() == 1);
    
    // Clear all
    stack.clear();
    assert(!stack.canUndo());
    assert(!stack.canRedo());
    assert(stack.undoCount() == 0);
    assert(stack.redoCount() == 0);
    
    std::cout << "✓ test_clear_stack passed" << std::endl;
}

void test_undo_redo_when_empty() {
    std::cout << "Running test_undo_redo_when_empty..." << std::endl;
    
    CommandStack stack;
    
    // Cannot undo/redo when stack is empty
    assert(!stack.undo());
    assert(!stack.redo());
    
    std::cout << "✓ test_undo_redo_when_empty passed" << std::endl;
}

int main() {
    std::cout << "Running mesh_core CommandStack tests..." << std::endl << std::endl;
    
    test_basic_undo_redo();
    test_multiple_undo_redo();
    test_redo_cleared_on_new_command();
    test_clear_stack();
    test_undo_redo_when_empty();
    
    std::cout << std::endl << "All tests passed! ✓" << std::endl;
    return 0;
}
