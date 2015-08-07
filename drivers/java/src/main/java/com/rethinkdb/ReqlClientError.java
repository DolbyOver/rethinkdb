// Autogenerated by metajava.py.
// Do not edit this file directly.
// The template for this file is located at:
// ../../../../../../templates/Exception.java
package com.rethinkdb;

import com.rethinkdb.ast.RqlAst;
import com.rethinkdb.response.Backtrace;
import java.util.*;

public class ReqlClientError extends ReqlError {

    Optional<Backtrace> backtrace = Optional.empty();
    Optional<RqlAst> term = Optional.empty();

    public ReqlClientError() {
    }

    public ReqlClientError(String message) {
        super(message);
    }

    public ReqlClientError(String format, Object... args) {
        super(String.format(format, args));
    }

    public ReqlClientError(String message, Throwable cause) {
        super(message, cause);
    }

    public ReqlClientError(Throwable cause) {
        super(cause);
    }

    public ReqlClientError(String msg, RqlAst term, Backtrace bt) {
        super(msg);
        this.backtrace = Optional.ofNullable(bt);
        this.term = Optional.ofNullable(term);
    }

    public ReqlClientError setBacktrace(Backtrace backtrace) {
        this.backtrace = Optional.ofNullable(backtrace);
        return this;
    }

    public Optional<Backtrace> getBacktrace() {
        return backtrace;
    }

    public ReqlClientError setTerm(RqlAst term) {
        this.term = Optional.ofNullable(term);
        return this;
    }

    public Optional<RqlAst> getTerm() {
        return this.term;
    }
}