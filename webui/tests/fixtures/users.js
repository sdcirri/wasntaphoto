export const ME = 1
export const OTHER = 42

export const ALICE = {
	userID: ME,
	username: 'alice',
	followers: 0,
	following: 0,
	posts: []
}

export const BOB = {
	userID: OTHER,
	username: 'bob',
	followers: 2,
	following: 1,
	posts: []
}

export const ALICE_POST = {
	postID: 10,
	author: ME,
	caption: 'hello from alice',
	likeCount: 0,
	comments: [],
	pubTime: Date.now() - 60_000
}

export const BOB_POST = {
	postID: 11,
	author: OTHER,
	caption: 'hello from bob',
	likeCount: 3,
	comments: [100],
	pubTime: Date.now() - 60_000
}

export const ALICE_COMMENT = {
	commentID: 100,
	author: ME,
	content: 'nice',
	likes: 0,
	time: Date.now() - 60_000
}

export const BOB_COMMENT = {
	commentID: 101,
	author: OTHER,
	content: 'cool pic',
	likes: 2,
	time: Date.now() - 60_000
}
