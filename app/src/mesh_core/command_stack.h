#ifndef MESH_CORE_COMMAND_STACK_H
#define MESH_CORE_COMMAND_STACK_H

#include <memory>
#include <stack>
#include <functional>

namespace mesh_core {

/**
 * Command interface for undo/redo operations
 */
class Command {
public:
    virtual ~Command() = default;
    virtual void execute() = 0;
    virtual void undo() = 0;
    virtual const char* getName() const = 0;
};

/**
 * CommandStack manages undo/redo operations
 */
class CommandStack {
public:
    CommandStack() = default;
    
    /**
     * Execute a command and add it to the undo stack
     * Clears the redo stack
     */
    void execute(std::unique_ptr<Command> cmd) {
        if (!cmd) return;
        
        cmd->execute();
        undo_stack_.push(std::move(cmd));
        
        // Clear redo stack when new command is executed
        while (!redo_stack_.empty()) {
            redo_stack_.pop();
        }
    }
    
    /**
     * Undo the last command
     */
    bool undo() {
        if (undo_stack_.empty()) {
            return false;
        }
        
        auto cmd = std::move(undo_stack_.top());
        undo_stack_.pop();
        
        cmd->undo();
        redo_stack_.push(std::move(cmd));
        
        return true;
    }
    
    /**
     * Redo the last undone command
     */
    bool redo() {
        if (redo_stack_.empty()) {
            return false;
        }
        
        auto cmd = std::move(redo_stack_.top());
        redo_stack_.pop();
        
        cmd->execute();
        undo_stack_.push(std::move(cmd));
        
        return true;
    }
    
    /**
     * Check if undo is available
     */
    bool canUndo() const {
        return !undo_stack_.empty();
    }
    
    /**
     * Check if redo is available
     */
    bool canRedo() const {
        return !redo_stack_.empty();
    }
    
    /**
     * Clear all undo/redo history
     */
    void clear() {
        while (!undo_stack_.empty()) {
            undo_stack_.pop();
        }
        while (!redo_stack_.empty()) {
            redo_stack_.pop();
        }
    }
    
    /**
     * Get the number of commands in undo stack
     */
    size_t undoCount() const {
        return undo_stack_.size();
    }
    
    /**
     * Get the number of commands in redo stack
     */
    size_t redoCount() const {
        return redo_stack_.size();
    }

private:
    std::stack<std::unique_ptr<Command>> undo_stack_;
    std::stack<std::unique_ptr<Command>> redo_stack_;
};

} // namespace mesh_core

#endif // MESH_CORE_COMMAND_STACK_H
