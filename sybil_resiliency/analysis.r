load_libraries <- function() {
	libs <- c('ggplot2', 'reshape2', 'stringr')
	for (lib in libs) {
		tryCatch(
			{
				require(lib, character.only=TRUE)
			},
			warning=function(cond) {
				install.packages(lib, repos="http://cran.us.r-project.org")
			}
		)

	}
}


renamed_protocols <- function(originals) {
	out <- c()
	for (original in originals) {
		out <- c(out,
			switch(original,
				   'pow'='Proof of Work',
				   'pos'='Proof of Stake',
				   'poa'='Proof of Authority',
				   'algorand'='Algorand Proof',
				   'conn_two'='Connitzer: Two Alternatives',
				   'conn_many'='Connitzer: Many Alternatives'))
	}
	return(out)
}


protocol_colors <- function(protocols) {
	out <- c()
	for (protocol in protocols) {
		out <- c(out,
				 switch(protocol,
				 	   'pow'='#1b9e77',
				 	   'pos'='#d95f02',
				 	   'poa'='#7570b3',
				 	   'algorand'='#e7298a',
				 	   'conn_two'='#66a61e',
				 	   'conn_many'='#e6ab02'))
	}
	return(out)
}


#' Fixes those columns of a frame that have zero variance.
#' 
#' @param frame The frame to fix the columns of, if these need fixing.
#' @return The fixed frame.
zero_variance_fixed_frame <- function(frame) {
	for (column in colnames(frame)) {
		if (sum(frame[, column] == 0.0) == nrow(frame)) {
			frame[, column] <- abs(jitter(frame[, column], factor=1e-8))
		}
	}
	return(frame)
}


#' Visualizes and yields per consensus protocol a distribution.
#'
#' @param file The path to the file. May be relative or absolute.
#' @param title The title of the plot.
#' @return A `ggplot2` plot object.
visualised_results <- function(file, title) {
	frame <- zero_variance_fixed_frame(read.csv(file))
	molten <- melt(frame, measure.vars=colnames(frame), value.name='sybil_prop')
	colnames(molten)[1] <- 'Protocol'
	plt <- ggplot(molten, mapping=aes_string(x='sybil_prop', color='Protocol'))
	plt <- plt + geom_density()
	plt <- plt +
		labs(title=title,
			 subtitle='Per-protocol density plot of fractions of total episodes in which sybils win') +
		xlab('Fraction of rounds in which sybils win') +
		ylab('Density')
	plt <- plt + scale_color_manual(name='Consensus Protocol',
									labels=renamed_protocols(colnames(frame)),
									values=protocol_colors(colnames(frame)))
	plt <- plt + coord_cartesian(xlim=c(0.0, 0.6), ylim=c(0.0, 75.0))
	plt <- plt + theme_light()
	return(plt)
}


main <- function() {
	load_libraries()
	results_dir <- paste0(getwd(), '/results')
	csvs <- list.files(results_dir, pattern='(\\.)(csv)')
	if (!dir.exists(paste0(getwd(), '/plots'))) {
		dir.create(paste0(getwd(), '/plots'))
	}
	for (csv in csvs) {
		num_honest <- str_extract_all(csv, '[0-9]++')[[1]][1]
		num_advers <- str_extract_all(csv, '[0-9]++')[[1]][2]
		file_name <- paste0(results_dir, '/', csv)
		plt <- visualised_results(
			file_name,
			paste0('Sybil resiliency: ', num_honest, ' honest users, ',
				   num_advers, ' adversaries'))
		save_loc <- paste0(getwd(),
						   '/plots/plot-for-',
						   str_replace(csv, '(\\.)(csv)', '.pdf'))
		ggsave(save_loc,
			   plot=plt,
			   device='pdf')
	}
	return('Success.')
}


main()
