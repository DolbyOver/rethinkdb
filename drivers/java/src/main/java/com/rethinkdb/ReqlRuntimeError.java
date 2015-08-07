// Autogenerated by metajava.py.
// Do not edit this file directly.
// The template for this file is located at:
// ../../../../../../templates/Exception.java
package com.rethinkdb;

import com.rethinkdb.ast.RqlAst;
import com.rethinkdb.response.Backtrace;
import java.util.*;

public class ReqlRuntimeError extends ReqlError {

    Optional<Backtrace> backtrace = Optional.empty();
    Optional<RqlAst> term = Optional.empty();

    public ReqlRuntimeError() {
    }

    public ReqlRuntimeError(String message) {
        super(message);
    }

    public ReqlRuntimeError(String format, Object... args) {
        super(String.format(format, args));
    }

    public ReqlRuntimeError(String message, Throwable cause) {
        super(message, cause);
    }

    public ReqlRuntimeError(Throwable cause) {
        super(cause);
    }

    public ReqlRuntimeError(String msg, RqlAst term, Backtrace bt) {
        super(msg);
        this.backtrace = Optional.ofNullable(bt);
        this.term = Optional.ofNullable(term);
    }

    public ReqlRuntimeError setBacktrace(Backtrace backtrace) {
        this.backtrace = Optional.ofNullable(backtrace);
        return this;
    }

    public Optional<Backtrace> getBacktrace() {
        return backtrace;
    }

    public ReqlRuntimeError setTerm(RqlAst term) {
        this.term = Optional.ofNullable(term);
        return this;
    }

    public Optional<RqlAst> getTerm() {
        return this.term;
    }
}