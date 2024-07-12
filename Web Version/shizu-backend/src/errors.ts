export class InvalidFileError extends Error {
    statusCode: number;
    constructor (message: string) {
        super(message);
        this.statusCode = 401;
    }
}

export class InvalidDjError extends Error {
    statusCode: number;
    constructor (message: string) {
        super(message);
        this.statusCode = 400;
    }
}

export class InvalidPromoError extends Error {
    statusCode: number;
    constructor (message: string) {
        super(message);
        this.statusCode = 400;
    }
}

export class InvalidLineupError extends Error {
    statusCode: number;
    constructor (message: string) {
        super(message);
        this.statusCode = 400;
    }
}

export class DjNotFoundError extends Error {
    statusCode: number;
    constructor (message: string) {
        super(message);
        this.statusCode = 404;
    }
}

export class PromoNotFoundError extends Error {
    statusCode: number;
    constructor (message: string) {
        super(message);
        this.statusCode = 404;
    }
}

export class LineupNotFoundError extends Error {
    statusCode: number;
    constructor (message: string) {
        super(message);
        this.statusCode = 404;
    }
}